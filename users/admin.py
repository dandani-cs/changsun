from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Customer, Employee

# Register your models here.
class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = "customer"

class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = "employee"

class CustomUserAdmin(UserAdmin):
    inlines = (CustomerInline, EmployeeInline,)
    list_display = ('email', 'first_name', 'last_name', 'is_customer', 'is_employee')

admin.site.register(User, CustomUserAdmin)
