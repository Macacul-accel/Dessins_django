from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import uuid
import random
from cloudinary.models import CloudinaryField
import cloudinary.uploader

from django.core.files import File
from django.db import models
from pathlib import Path

from user.models import MyUser

FONT_PATH = Path(__file__).resolve().parent / 'font' / 'open_sans.ttf'

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
            
    def make_thumbnail(self, image, size=(300, 200)):
        """
        Generate a thumbnail from the original watermarked image.
        """
        img = Image.open(image)
        img.thumbnail(size, Image.LANCZOS)

        thumb_io = BytesIO()
        img.save(thumb_io, format='PNG', quality=85)
        thumb_io.seek(0)

        result = cloudinary.uploader.upload(thumb_io, folder='thumbnails/')
        return result['secure_url']

    def resize_image(self, image, size=(600, 800)):
        """
        Resize the uploaded image to display constant image
        """
        img = Image.open(image)
        img = img.resize(size, Image.LANCZOS)

        img_io = BytesIO()
        img.save(img_io, format='PNG', quality=85)
        img_io.seek(0)

        return img_io
    
    def add_watermark(self, image):
        """
        Add a watermark to the image and upload it to Cloudinary
        """
        img = Image.open(image).convert('RGBA')
        watermark_text = "@nathalielncle"
        font = ImageFont.truetype(FONT_PATH, 50)

        width, height = img.size

        # Create a single watermark tile
        text_bbox = font.getbbox(watermark_text)
        tile_size = (text_bbox[2] + 20, text_bbox[3] + 20)
        tile = Image.new("RGBA", tile_size, (0, 0, 0, 0))

        draw = ImageDraw.Draw(tile)
        draw.text((10, 10), watermark_text, font=font, fill=(51, 51, 51))
        tile = tile.rotate(-30, expand=True)  # Rotate before tiling
        
        # Create watermark layer
        watermark = Image.new('RGBA', img.size, (0, 0, 0, 0))
        for x in range(0, width, tile.width + 50):
            for y in range(0, height, tile.height + 50):
                watermark.paste(tile, (x, y), tile)


        # Adding the watermark layer to the original image
        watermarked_img = Image.alpha_composite(img, watermark).convert('RGB')

        temp_img = BytesIO()
        watermarked_img.save(temp_img, 'PNG')
        temp_img.seek(0)

        return temp_img
        
    def save(self, *args, **kwargs):
        """
        Resize and watermark before uploading to cloudinary
        """
        if self.image and not self.pk:
            resized_img = self.resize_image(self.image)
            watermarked_img = self.add_watermark(resized_img)

            img_result = cloudinary.uploader.upload(watermarked_img, folder='watermarked/')
            self.image = img_result['secure_url']

            thumbnail_img = self.make_thumbnail(watermarked_img)
            thumb_result = cloudinary.uploader.upload(thumbnail_img, folder='thumbnails/')
            self.thumbnail = thumb_result['secure_url']

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
    payment_token = models.CharField(max_length=100, null=True, blank=True)
    
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
