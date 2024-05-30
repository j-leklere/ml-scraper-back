from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50)

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

class Product(models.Model):
    name = models.CharField(max_length=150)
    url = models.CharField(max_length=500)
    image_url = models.CharField(max_length=500)
    price_ars = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    discount = models.IntegerField(null=True)
    currency = models.CharField(max_length=10)
    is_own = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Search(models.Model):
    name = models.CharField(max_length=100)
    term = models.CharField(max_length=100)
    results = models.IntegerField()
    last_searched_at = models.DateField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)