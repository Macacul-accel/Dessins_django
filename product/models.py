from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import uuid
import os
from cloudinary.models import CloudinaryField
import cloudinary.uploader

from django.core.files import File
from django.db import models

from user.models import MyUser

class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.slug}/'
    
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = CloudinaryField(folder='watermarked/', blank=True, null=True)
    thumbnail = CloudinaryField(folder='thumbnails/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_added',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'
    
    def get_image(self):
        if self.image:
            return self.image.url
        return ''
        
    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return self.thumbnail.url
            else:
                return ''
            
    def make_thumbnail(self, image, size=(300, 200)):
        """
        Generate a thumbnail from the original watermarked image.
        """
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)

        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)

        thumbnail = File(thumb_io, name=image.name)

        return thumbnail

    def resize_image(self, image):
        """
        Resize the uploaded image to display constant image
        """
        img = Image.open(image)
        img = img.resize((600, 800), Image.ANTIALIAS)

        temp_img = 'temp_resized_img.png'
        img.save(temp_img, 'PNG')

        return temp_img
    
    def add_watermark(self, image):
        """
        Add a watermark to the image and upload it to Cloudinary
        """
        watermark_text = "@nathalielncle"

        img = Image.open(image).convert('RGBA')
        width, height = img.size

        # Watermark layer
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark)

        #Define the font
        try:
            font = ImageFont.truetype('arial.ttf', size=50)
        except IOError:
            # Default font if not available
            font = ImageFont.load_default()

        text_width, text_height = draw.textsize(watermark_text, font)

        # Space between tiles
        spacing_x = text_width + 50
        spacing_y = text_height + 50

        # Till watermark_text all over the image
        for x in range(0, width, spacing_x):
            for y in range(0, height, spacing_y):
                # temporary layer for the tiles
                tile = Image.new('RGBA', img.size, (0, 0, 0, 0))
                tile_draw = ImageDraw.Draw(tile)

                # Make the tile transparent and pivot
                tile_draw.text((x, y), watermark_text, font=font, fill=(0, 0, 0, 128))
                tile = tile.rotate(-30, expand=True, resample=Image.BICUBIC, center=(x, y))

                # Adding the tile to the layer
                watermark = Image.alpha_composite(watermark, tile)

        # Adding the watermark layer to the original image
        watermarked_img = Image.alpha_composite(img, watermark)

        # Saving the image temporarily
        temp_img = "temp_watermarked_img.png"
        watermarked_img.save(temp_img, 'PNG')

        result = cloudinary.uploader.upload(temp_img, folder='watermarked/')
        os.remove(temp_img)

        # Return the cloudinary url of the watermarked image
        return result['secure_url']

    def save(self, *args, **kwargs):
        """
        Override the save method to add a watermark to the original image after resizing it.
        """
        if self.image:
            resized_img = self.resize_image(self.image)
            self.image = self.add_watermark(resized_img)

            os.remove(resized_img)
        super().save(*args, **kwargs)

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'En cours'
        CONFIRMED = 'Confirmée'
        CANCELLED = 'Annulée'

    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    shipping_details = models.JSONField(null=True, blank=True)
    payment_token = models.CharField(max_length=100)
    
    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Commande #{self.order_id}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
