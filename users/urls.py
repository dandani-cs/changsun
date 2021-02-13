from django.urls import path

from .views import CustomerSignUpView, EmployeeAddView, UserLoginView, ProfileView, CustomerEditProfileView, EditUserPasswordView
from django.views.generic.base import TemplateView

urlpatterns = [
               path("login", UserLoginView.as_view(), name="final_login"),
               path("edit_customer_profile", CustomerEditProfileView.as_view(), name="customer_edit_profile"),
               path("edit_user_password", EditUserPasswordView.as_view(), name = "user_edit_password"),
               path("signup", CustomerSignUpView.as_view(), name="customer_signup"),
               path("add_employee", EmployeeAddView.as_view(), name="employee_add"),
               path("profile", ProfileView.as_view(), name="profile"),
]
