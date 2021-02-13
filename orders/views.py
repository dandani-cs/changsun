from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Order
from users.models import Customer, User
from .forms import BaseOrderForm, UnregisteredUserForm, UnregisteredCustomerForm, ReceivedOrderForm

# Create your views here.
class OrderListView(LoginRequiredMixin, ListView):
    login_url = 'final_login'
    redirect_field_name = 'redirect_to'
    model = Order
    template_name = "orders.html"

    def get_queryset(self):
        if self.request.user.is_customer:
            customer = Customer.objects.get(user=self.request.user)
            queryset = customer.order_set.all()
        else:
            queryset = Order.objects.all()

        return queryset


class OrderCreateView(LoginRequiredMixin, View):
    login_url = 'final_login'
    redirect_field_name = 'redirect_to'
    template_name = "order_create_new.html"

    def post(self, request, *args, **kwargs):
        customer_uid      = (request.session['uname_create_order_existing'] if 'uname_create_order_existing' in request.session else 0)
        customuser_form = UnregisteredUserForm(request.POST, prefix='customuser_form')
        customeruser_form = UnregisteredCustomerForm(request.POST, prefix='customeruser_form')
        baseorder_form = BaseOrderForm(request.POST, prefix="baseorder_form")

        if baseorder_form.is_valid():
            order_form = baseorder_form.save(commit=False)

            if request.user.is_employee or request.user.is_superuser:
                if customer_uid:
                    custom_user         = get_customer_by_uuid(customer_uid)
                    customer            = Customer.objects.get(user = custom_user)
                    order_form.customer = customer
                    del request.session['uname_create_order_existing']

                elif customuser_form.is_valid() and customeruser_form.is_valid():
                    uform = customuser_form.save(commit=False)
                    uform.is_customer = True
                    uform.save()

                    cuform = customeruser_form.save(commit=False)
                    cuform.user = uform
                    cuform.save()

                    order_form.customer = cuform

                else:
                    return render(request, 'order_create_new.html', {
                                                    'baseorder_form'   : baseorder_form,
                                                    'customuser_form'  : customuser_form,
                                                    'customeruser_form': customeruser_form,
                                                    'customer_uuid_opt': 0
                                                })

            elif request.user.is_customer:
                order_form.customer = request.user.customer

            # FILLER VALUES
            order_form.delivery_price = 0
            order_form.service_price = 0
            order_form.weight = 0

            order_form.save()

            if order_form.status == 1:
                return HttpResponseRedirect(reverse_lazy('order_view'))
            else:
                return HttpResponseRedirect(reverse_lazy('order_received', kwargs = {'ref_id': order_form.ref_id}))

        else:
            return render(request, 'order_create_new.html', {'baseorder_form': baseorder_form, 'customuser_form': customuser_form, 'customeruser_form': customeruser_form})


    def get(self, request, uid = None):
        customer_uid      = (request.session['uname_create_order_existing'] if 'uname_create_order_existing' in request.session else 0)
        customuser_form = None
        customeruser_form = None

        if request.user.is_employee or request.user.is_superuser:
            if customer_uid:
                print("UID:", customer_uid)
            else:
                customuser_form = UnregisteredUserForm(prefix='customuser_form')
                customeruser_form = UnregisteredCustomerForm(prefix='customeruser_form')

        baseorder_form = BaseOrderForm(prefix="baseorder_form")
        return render(request, 'order_create_new.html', {
                                        'baseorder_form'   : baseorder_form,
                                        'customuser_form'  : customuser_form,
                                        'customeruser_form': customeruser_form,
                                        'customer_uuid_opt': uid,
                                        'existing_customer': True if customer_uid else False
                                    })


class ReceivedOrderView(LoginRequiredMixin, View):
    def get(self, request, ref_id):
        order = get_order_by_ref_id(ref_id)
        received_form = ReceivedOrderForm(instance = order, prefix="received_form")

        return render(request, 'order_received.html', {'received_form': received_form} )

    def post(self, request, ref_id):
        received_form = ReceivedOrderForm(request.POST, prefix='received_form')

        order = get_order_by_ref_id(ref_id)

        if received_form.is_valid():
            order.service_price = received_form.cleaned_data.get("service_price")
            order.weight = received_form.cleaned_data.get("weight")

            order.save()

            return HttpResponseRedirect(reverse_lazy('order_view'))

        else:
            return render(request, 'order_received.html', {'received_form': received_form})


class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, ref_id):
        return render(request, 'order_details.html', {'order': get_order_by_ref_id(ref_id)})



class OrderOptionView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_employee or request.user.is_superuser:
            return render(request, 'order_option.html')

        return HttpResponseRedirect(reverse_lazy('order_new'))


class CustomerSearchView(ListView):
    model = Customer
    template_name = "user_search.html"

    def get_queryset(self):
        query     = self.request.GET.get('query')
        filter_by = self.request.GET.get('filter')
        if query:
            if filter_by == "name":
                return Customer.objects.filter( Q( user__first_name__contains = query ) |
                                                Q( user__last_name__contains  = query ) )
            else:
                return Customer.objects.filter( Q( user__email__contains = query) )

        else:
            return Customer.objects.all()

    def post(self, request):
        username = self.request.POST.get('username')
        request.session['uname_create_order_existing'] = username.strip()
        return HttpResponseRedirect(reverse_lazy("order_new"))



def get_customer_by_uuid(uuid):
    try:
        return User.objects.get(username = uuid)
    except User.DoesNotExist:
        return None


def get_order_by_ref_id(id):
    try:
        return Order.objects.get(ref_id = id)
    except Order.DoesNotExist:
        return None
