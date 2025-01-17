from django.contrib import admin

from .models import Category, Product, Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]


admin.site.register(Order, OrderAdmin)
admin.site.register(Category)
admin.site.register(Product)
