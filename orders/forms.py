from django import forms

from .models import Order
from users.models import User, Customer
from django.utils.translation import ugettext_lazy as _


class BaseOrderForm(forms.ModelForm):

    class Meta:
        model = Order
        fields = ('provision_type', 'retrieval_type', 'service', 'address', 'status', 'comments')
        widgets = {
                   "provision_type": forms.Select(attrs={'class': "custom-select my-1 mr-sm-2", 'id': 'inputProvision'}),
                   "retrieval_type": forms.Select(attrs={'class': "custom-select my-1 mr-sm-2", 'id': 'inputRetrieval'}),
                   "service": forms.Select(attrs={'class': "custom-select my-1 mr-sm-2"}),
                   "address": forms.TextInput(attrs = {"class": "form-control", 'id': 'add'}),
                   "status": forms.Select(attrs={'class': "custom-select my-1 mr-sm-2"}),
                   "comments": forms.Textarea(attrs={'class': "form-control"})
        }


class UnregisteredUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ( 'first_name', 'last_name')

        widgets = {
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
        fields = ('weight',)

        widgets = {
                   "weight": forms.NumberInput(attrs={'class': "form-control"}),
        }
