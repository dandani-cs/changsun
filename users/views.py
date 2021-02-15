from django.shortcuts import render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .forms import UserForm, CustomerUserForm, EmployeeUserForm, EditUserForm, CustomerEditForm
from .models import User, Customer

# Create your views here.
class AdminStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


class CustomerSignUpView(View):
    template_name = 'signup.html'

    def post(self, request, *args, **kwargs):
        customuser_form = UserForm(request.POST, prefix='customuser_form')
        customeruser_form = CustomerUserForm(request.POST, prefix='customeruser_form')

        if customuser_form.is_valid() and customeruser_form.is_valid():
            uform = customuser_form.save(commit=False)
            password = customuser_form.cleaned_data['password']

            uform.set_password(password)
            uform.is_customer = True

            uform.save()

            cuform = customeruser_form.save(commit=False)
            cuform.user = uform
            cuform.save()

            return HttpResponseRedirect(reverse_lazy('signup_confirmed'))

        else:
            return render(request, 'signup.html', {'customuser_form': customuser_form, 'customeruser_form': customeruser_form})

    def get(self, request):
        customuser_form = UserForm(prefix='customuser_form')
        customeruser_form = CustomerUserForm(prefix='customeruser_form')
        return render(request, 'signup.html', {'customuser_form': customuser_form, 'customeruser_form': customeruser_form})


class EmployeeAddView(LoginRequiredMixin, View):
    login_url = 'final_login'
    redirect_field_name = 'redirect_to'
    template_name = 'employee_add.html'

    def post(self, request, *args, **kwargs):
        customuser_form = UserForm(request.POST, prefix='customuser_form')
        employeeuser_form = EmployeeUserForm(request.POST, prefix='employeeuser_form')

        if customuser_form.is_valid() and employeeuser_form.is_valid():
            uform = customuser_form.save(commit=False)
            password = customuser_form.cleaned_data['password']

            uform.set_password(password)
            uform.is_employee = True

            uform.save()

            euform = employeeuser_form.save(commit=False)
            euform.user = uform
            euform.save()

            return HttpResponseRedirect(reverse_lazy('home'))

        else:
            return render(request, 'employee_add.html', {'customuser_form': customuser_form, 'employeeuser_form': employeeuser_form})

    def get(self, request):
        if not request.user.is_superuser:
            return HttpResponseRedirect(reverse_lazy('invalid'))

        customuser_form = UserForm(prefix='customuser_form')
        employeeuser_form = EmployeeUserForm(prefix='employeeuser_form')
        return render(request, 'employee_add.html', {'customuser_form': customuser_form, 'employeeuser_form': employeeuser_form})


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_authenticated:
            if request.user.is_customer:
                userinfo = {
                        "user_email": request.user.email,
                        "name": request.user.first_name + " " + request.user.last_name,
                        "contact": request.user.customer.contact,
                        "saved_address": request.user.customer.saved_address
                }

            elif request.user.is_employee:
                userinfo = {
                        "user_email": request.user.email,
                        "name": request.user.first_name + " " + request.user.last_name,
                        "start_date": request.user.employee.start_date
                }

            elif request.user.is_superuser:
                userinfo = {
                        "user_email": request.user.email,
                        "name": request.user.first_name + " " + request.user.last_name,
                }

            return render(request, 'profile.html', userinfo)
        else:
            return HttpResponseRedirect(reverse_lazy('final_login'))



class CustomerEditProfileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        customer        = get_customer(request.user)
        customer_form   = CustomerEditForm(request.POST, instance = customer)
        customuser_form = EditUserForm(request.POST, instance = request.user)

        if customuser_form.is_valid() and customer_form.is_valid():
            customuser_form.save()
            customer_form.save()

            return HttpResponseRedirect(reverse_lazy('profile'))
        else:
            return render(request, 'profile_edit.html', {
                    'customuser_form': customuser_form,
                    'customer_form'  : customer_form,
                })

    def get(self, request):
        customer        = get_customer(request.user)
        customer_form   = CustomerEditForm(instance = customer)
        customuser_form = EditUserForm(instance = request.user)

        return render(request, 'profile_edit.html', {
                'customuser_form': customuser_form,
                'customer_form'  : customer_form,
            })


class UserLoginView(View):
    def post(self, request, *args, **kwargs):
        email = request.POST['email']
        password = request.POST['password']
        username = get_user(email)
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse_lazy('order_view'))

        else:
            return render(request, 'registration/login.html', {'error': True})

    def get(self, request):
        return render(request, 'registration/login.html', {'error': False})


class EditUserPasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        password_form = PasswordChangeForm(request.user, request.POST)

        if password_form.is_valid():
            password_form.save()
            return HttpResponseRedirect(reverse_lazy('home'))
        else:
            return render(request, 'registration/password_change_form.html', {
                    'password_form': password_form
                })

    def get(self, request):
        password_form   = PasswordChangeForm(request.user)

        return render(request, 'registration/password_change_form.html', {
                'password_form': password_form
            })


def get_user(email):
    try:
        return User.objects.get(email=email.lower())
    except User.DoesNotExist:
        return None

def get_customer(custom_user):
    try:
        return Customer.objects.get(user=custom_user)
    except Customer.DoesNotExist:
        return None
