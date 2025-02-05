from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import uuid

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
    image = models.ImageField(upload_to='originals/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_added',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'
    
    def get_image(self):
        if self.image:
            return 'https://dessins-api.onrender.com' + self.image.url
        return ''
        
    def get_thumbnail(self):
        if self.thumbnail:
            return 'https://dessins-api.onrender.com' + self.thumbnail.url
        else:
            if self.image:
                self.thumbnail = self.make_thumbnail(self.image)
                self.save()

                return 'https://dessins-api.onrender.com' + self.thumbnail.url
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

    def add_watermark(self, image, watermark_text="@nathalielncle", position=(10, 10), font_size=20):
        """
        Add a watermark to the original image before saving.
        """
        img = Image.open(image).convert('RGB')
        watermark = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        watermark.text(position, watermark_text, fill=(255, 255, 255, 128), font=font)
        
        watermarked_io = BytesIO()
        img.save(watermarked_io, 'JPEG', quality=85)
        return File(watermarked_io, name=image.name)

    def save(self, *args, **kwargs):
        """
        Override the save method to add a watermark to the original image.
        """
        if self.image:
            self.image = self.add_watermark(self.image)
        
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
