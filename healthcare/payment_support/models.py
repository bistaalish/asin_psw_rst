from pyexpat.errors import messages
from django.db import models
from django.contrib.auth.models import User



class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    index = models.PositiveIntegerField(unique=True)
    
    def __str__(self):
        return self.name


class Order(models.Model):
    # customer_name = models.CharField(max_length=100)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Correct reference to Package model
    timestamp = models.DateTimeField(auto_now_add=True)
    is_pending = models.BooleanField(default=True)

    def __str__(self):
        return f"Order for {self.customer}"


class Purchase(models.Model):
    buyer_name = models.CharField(max_length=255)
    email = models.EmailField()
    # product = models.ForeignKey(Package, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    
    SINGLE_PRODUCT = 'single package'
    ALL_PRODUCT = 'all package'
    
    PAYMENT_CHOICES = (
        (SINGLE_PRODUCT, 'buy one'),
        (ALL_PRODUCT, 'buy all'),
    )

    method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    stage1 = models.BooleanField(default=False)
    stage2 = models.BooleanField(default=False)
    stage3 = models.BooleanField(default=False)
    score_result_1 = models.IntegerField(default=0)
    score_result_2 = models.IntegerField(default=0)
    score_result_3 = models.IntegerField(default=0)
    diagnosis = models.TextField(blank=True, null=True)

    def is_paid(self):
        return self.stage1 and self.stage2 and self.stage3

    is_paid.boolean = True  # Display as a boolean (green/red) in admin panel
    is_paid.short_description = 'Paid'
