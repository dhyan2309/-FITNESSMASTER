from django.contrib import admin
from .models import *
# Register your models here.


class UserProfile_(admin.ModelAdmin):
    list_display = ('user', 'role', 'email', 'phone_number')


class Package_(admin.ModelAdmin):
    list_display = ('package_name', 'duration', 'description','price')


class Trainer_(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'training_category', 'specialization')

   
class Customer_(admin.ModelAdmin):
    list_display = ('user', 'date_of_birth', 'gender', 'address', 'assigned_package', 'assigned_trainer', 'start_date', 'end_date')


class Dietplan_(admin.ModelAdmin):
    list_display = ('customer', 'trainer', 'description')


class Exerciseplan_(admin.ModelAdmin):
    list_display = ('customer', 'trainer', 'exercises','category')


class Payment_(admin.ModelAdmin):
    list_display = ('customer', 'amount', 'payment_date', 'payment_method')


class Equipment_(admin.ModelAdmin):
    list_display = ('name', 'category', 'quantity', 'status', 'purchase_date', 'last_maintenance')


class Enquiry_(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status',)


admin.site.register(UserProfile,UserProfile_)
admin.site.register(Package,Package_)
admin.site.register(Trainer,Trainer_)
admin.site.register(Customer,Customer_)
admin.site.register(Dietplan,Dietplan_)
admin.site.register(Exerciseplan,Exerciseplan_)
admin.site.register(Payment,Payment_)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Notice)
admin.site.register(Feedback)
admin.site.register(Equipment, Equipment_)
admin.site.register(Enquiry, Enquiry_)
