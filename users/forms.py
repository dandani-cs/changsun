from django import forms
from django.db import transaction
from django.utils.translation import ugettext_lazy as _

from .models import User, Customer, Employee

class UserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Confirm Password"}))

    class Meta:
        model = User
        fields = ('email', 'password', 'confirm_password', 'first_name', 'last_name',)
        widgets = {
                   'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Enter Password"}),
                   'confirm_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Confirm Password"}),
                   'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter e-mail", 'required': 'required'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter First Name"}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Last Name"}),
        }


    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError(
                "password and confirm_password does not match"
            )

        email = cleaned_data.get("email")

        if email == "":
            raise forms.ValidationError("Please input your email")



class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


        widgets = {
                   'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter e-mail", 'required': 'required'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter First Name"}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Last Name"}),
        }


class CustomerUserForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ('contact',)

        widgets = {
                   'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Contact Number"}),
        }

        labels = {
                  'contact': _("Contact Number"),
        }


class CustomerEditForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('contact', 'saved_address')

        widgets = {
                   'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Contact Number"}),
                   'saved_address': forms.TextInput (attrs={'class': 'form-control', 'placeholder': "Enter Home Address"})
        }

        labels = {
                  'contact': _("Contact Number"),
                  'saved_address': _("Home Address")
        }



class EmployeeUserForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ('start_date',)

        widgets = {
                   'start_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Start Date"})
        }

        labels = {
                  'start_date': _('Start date:')
        }
