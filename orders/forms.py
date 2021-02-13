from django import forms

from .models import Order
from users.models import User, Customer
from django.utils.translation import ugettext_lazy as _


class BaseOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('provision_type', 'retrieval_type', 'service', 'address', 'status')
        widgets = {
                   "provision_type": forms.Select(attrs={'class': "custom-select my-1 mr-sm-2", 'id': 'provision-choice'}),
                   "retrieval_type": forms.Select(attrs={'class': "custom-select my-1 mr-sm-2", 'id': 'retrieval-choice'}),
                   "service": forms.Select(attrs={'class': "custom-select my-1 mr-sm-2"}),
                   "address": forms.TextInput(attrs = {"class": "form-control", 'id': 'address-input'}),
                   "status": forms.Select(attrs={'class': "form-control"}),
        }


class UnregisteredUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')

        widgets = {
                   'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter e-mail", 'required': 'required'}),
                   'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter First Name"}),
                   'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Last Name"}),
        }


class UnregisteredCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('contact',)

        widgets = {
                   'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter Contact Number"})
        }

        labels = {
                  'contact': _("Contact Number")
        }


class ReceivedOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('service_price', 'weight')

        widgets = {
                   "service_price": forms.TextInput(attrs={'class': "form-control"}),
                   "weight": forms.NumberInput(attrs={'class': "form-control"}),
        }

        labels = {
                  'service_price': _("Service Price:")
        }
