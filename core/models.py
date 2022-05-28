from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Product(models.Model):
    CATEGORY = (
			('uttara', 'uttara'),
			('badda', 'badda'),
			) 
    shopname = models.CharField(max_length=200, null=True, choices=CATEGORY)        
    name = models.CharField(max_length=200)
    price = models.DecimalField(
        decimal_places=0,
        max_digits=10,
        validators=[MinValueValidator(0)]
    )
    quantity = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.name+"  quantity"+self.quantity 

class UserItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return self.product.name