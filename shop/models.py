from django.db import models

class LoginAttempt(models.Model):
    username = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(default="Unknown")
    timestamp = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=False)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=10)
    def __str__(self):
        return self.name

class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    def __str__(self):
        return self.username

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email = models.EmailField(unique=True)
    saved_card_number = models.CharField(max_length=19)
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order {self.id}"
    def total(self):
        return sum(item.quantity * item.product.price for item in self.orderitem_set.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)