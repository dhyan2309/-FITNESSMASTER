from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin',    'Admin'),
        ('trainer',  'Trainer'),
        ('customer', 'Customer'),
    ]
    user         = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name    = models.CharField(max_length=100)
    email        = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=10)
    role         = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return self.full_name


class Package(models.Model):
    duartion_choices = [
        (1,  '1 month'),
        (3,  '3 months'),
        (6,  '6 months'),
        (12, '12 months'),
    ]
    package_name = models.CharField(max_length=100)
    duration     = models.IntegerField(choices=duartion_choices)
    description  = models.TextField()
    price        = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.package_name


class Trainer(models.Model):
    CATEGORY_CHOICES = [
        ('Yoga',  'Yoga'),
        ('Gym',   'Gym'),
        ('Zumba', 'Zumba'),
    ]
    user              = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name         = models.CharField(max_length=100)
    training_category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    specialization    = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.full_name


class Customer(models.Model):
    user             = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name        = models.CharField(max_length=100)
    date_of_birth    = models.DateField(null=True, blank=True)
    gender           = models.CharField(max_length=10, blank=True)
    address          = models.CharField(max_length=200, blank=True)
    assigned_package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True, blank=True)
    start_date       = models.DateField(null=True, blank=True)
    end_date         = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.full_name


class Dietplan(models.Model):
    trainer     = models.ForeignKey(Trainer,  on_delete=models.CASCADE)
    customer    = models.ForeignKey(Customer, on_delete=models.CASCADE)
    description = models.TextField()
    calories    = models.IntegerField()

    def __str__(self):
        return f"Diet - {self.customer} by {self.trainer}"


class Exerciseplan(models.Model):
    trainer   = models.ForeignKey(Trainer,  on_delete=models.CASCADE)
    customer  = models.ForeignKey(Customer, on_delete=models.CASCADE)
    title     = models.CharField(max_length=100)
    exercises = models.TextField()
    category  = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.title} - {self.customer}"


class Payment(models.Model):
    customer       = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date   = models.DateField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.customer.full_name} - {self.amount}"


class Product(models.Model):
    product_name = models.CharField(max_length=100)
    description  = models.TextField()
    price        = models.DecimalField(max_digits=10, decimal_places=2)
    stock        = models.IntegerField()
    image        = models.ImageField(upload_to='product_images/', blank=True, null=True)

    def __str__(self):
        return self.product_name


class Order(models.Model):
    customer    = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product     = models.ForeignKey(Product,  on_delete=models.CASCADE)
    quantity    = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.customer} - {self.product} x{self.quantity}"


class Notice(models.Model):
    RECIPIENT_CHOICES = [
        ('all',      'All Users'),
        ('customer', 'Customers Only'),
        ('trainer',  'Trainers Only'),
    ]
    title   = models.CharField(max_length=100)
    message = models.TextField()
    sent_to = models.CharField(max_length=20, choices=RECIPIENT_CHOICES, default='all')

    def __str__(self):
        return self.title


class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    message  = models.TextField()
    rating   = models.IntegerField()

    def __str__(self):
        return f"{self.customer.full_name} - {self.rating} Stars"


class BodyRecord(models.Model):
    customer   = models.ForeignKey(Customer, on_delete=models.CASCADE)
    weight_kg  = models.DecimalField(max_digits=5, decimal_places=2)
    height_cm  = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_on = models.DateField(auto_now_add=True)
    note        = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.customer.full_name} — {self.recorded_on}"

    @property
    def bmi(self):
        try:
            height_m = float(self.height_cm) / 100
            bmi_val  = float(self.weight_kg) / (height_m ** 2)
            return round(bmi_val, 1)
        except:
            return None

    @property
    def bmi_category(self):
        b = self.bmi
        if b is None:
            return '—'
        if b < 18.5:
            return 'Underweight'
        elif b < 25:
            return 'Normal'
        elif b < 30:
            return 'Overweight'
        else:
            return 'Obese'
        
class Invoice(models.Model):
    customer     = models.ForeignKey(Customer, on_delete=models.CASCADE)
    payment      = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_no   = models.CharField(max_length=20, unique=True)
    generated_on = models.DateField(auto_now_add=True)
    notes        = models.TextField(blank=True)

    def __str__(self):
        return f"Invoice #{self.invoice_no} — {self.customer.full_name}"


class Equipment(models.Model):
    CATEGORY_CHOICES = [
        ('Cardio',        'Cardio'),
        ('Strength',      'Strength'),
        ('Free Weights',  'Free Weights'),
        ('Functional',    'Functional'),
        ('Other',         'Other'),
    ]
    STATUS_CHOICES = [
        ('Working',           'Working'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Out of Order',      'Out of Order'),
    ]
    name             = models.CharField(max_length=100)
    category         = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description      = models.TextField(blank=True)
    quantity         = models.IntegerField(default=1)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Working')
    purchase_date    = models.DateField(null=True, blank=True)
    last_maintenance = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name


class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('New',          'New'),
        ('In Progress',  'In Progress'),
        ('Resolved',     'Resolved'),
    ]
    full_name  = models.CharField(max_length=100)
    email      = models.EmailField()
    phone      = models.CharField(max_length=15)
    message    = models.TextField()
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Enquiries'

    def __str__(self):
        return f"{self.full_name} — {self.status}"
