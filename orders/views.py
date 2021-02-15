from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import LoginRequiredMixin

import math
from .models import Order, OrderService
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
                    uform.email = None
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
            dist_num = float(request.POST['dist_num'])
            if dist_num > 1:
                order_form.delivery_price = math.ceil(dist_num) * 20
            else:
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
        if not request.user.is_employee and not request.user.is_superuser:
            return HttpResponseRedirect(reverse_lazy('invalid'))

        order = get_order_by_ref_id(ref_id)
        received_form = ReceivedOrderForm(instance = order, prefix="received_form")
        is_service_products = (order.service == OrderService.SERVICE_LP)

        return render(request, 'order_received.html', {
                    'received_form'  : received_form,
                    'is_laundro_prod': is_service_products
                })

    def post(self, request, ref_id):
        received_form = ReceivedOrderForm(request.POST, prefix='received_form')

        order = get_order_by_ref_id(ref_id)

        BASE_SERVICE_PRICE = {
                    OrderService.SERVICE_WD  : 185,
                    OrderService.SERVICE_WDF : 185,
                    OrderService.SERVICE_DC  : 75,
                    OrderService.SERVICE_LP  : 15,
                    OrderService.SERVICE_W   : 50,
                    OrderService.SERVICE_D   : 60,
                    OrderService.SERVICE_F   : 25,
                    OrderService.SERVICE_SD  : 75,
                }

        PER_LOAD_SERVICES = [
                    OrderService.SERVICE_WD,
                    OrderService.SERVICE_W,
                    OrderService.SERVICE_D,
                    OrderService.SERVICE_WDF
                ]


        if received_form.is_valid():
            order.weight = received_form.cleaned_data.get("weight")
            base_price   = BASE_SERVICE_PRICE[order.service]

            if order.service in PER_LOAD_SERVICES:
                additional = (BASE_SERVICE_PRICE[OrderService.SERVICE_F] if order.service == OrderService.SERVICE_WDF else 0)
                load       = math.ceil(order.weight / 8)
                print("Computed ({}) loads".format(load))

                order.service_price = load * base_price + additional
            else:
                order.service_price = base_price * order.weight

            print("Service ({}), Weight: ({}), Base Price ({})".format(order.service, order.weight, base_price))
            print("Computed service price: ({})".format(order.service_price))

            order.status = 2

            order.save()


            return HttpResponseRedirect(reverse_lazy('order_view'))

        else:
            return render(request, 'order_received.html', {'received_form': received_form})



class OrderDetailView(LoginRequiredMixin, View):
    def get(self, request, ref_id):
        order = get_order_by_ref_id(ref_id)
        if not request.user.is_employee and not request.user.is_superuser and (request.user != order.customer.user):
            return HttpResponseRedirect(reverse_lazy('invalid'))


        print(order.status)
        return render(request, 'order_details.html', {'order': order,
                                                      'order_status_name': ['Fetch', 'Received', 'Confirm', 'Processing', 'Ready', 'Given', ''][order.status]
                                                      })


    def post(self, request, ref_id):
        order = get_order_by_ref_id(ref_id)
        order.status += 1

        order.save()

        return HttpResponseRedirect(reverse_lazy('order_detail', kwargs = {'ref_id': order.ref_id}))


class OrderEditView(LoginRequiredMixin, View):
    login_url = 'final_login'
    redirect_field_name = 'redirect_to'
    template_name = "order_create_new.html"

    def post(self, request, ref_id, *args, **kwargs):
        prev_order = get_order_by_ref_id(ref_id)
        customer_uid      = (request.session['uname_create_order_existing'] if 'uname_create_order_existing' in request.session else 0)
        customuser_form = UnregisteredUserForm(request.POST, prefix='customuser_form', instance = prev_order)
        customeruser_form = UnregisteredCustomerForm(request.POST, prefix='customeruser_form', instance = prev_order)
        baseorder_form = BaseOrderForm(request.POST, prefix="baseorder_form", instance = prev_order)

        if baseorder_form.is_valid():
            order_form = baseorder_form.save(commit=False)

            if request.user.is_employee or request.user.is_superuser:

                if customuser_form.is_valid() and customeruser_form.is_valid():
                    uform = customuser_form.save(commit=False)
                    uform.is_customer = True
                    uform.email = None
                    uform.save()

                    cuform = customeruser_form.save(commit=False)
                    cuform.user = uform
                    cuform.save()

                    order_form.customer = prev_order.customer

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

            order_form.delivery_price = prev_order.delivery_price
            order_form.service_price = prev_order.service_price
            order_form.weight = prev_order.weight

            order_form.save()

            if order_form.status == 1:
                return HttpResponseRedirect(reverse_lazy('order_view'))
            else:
                return HttpResponseRedirect(reverse_lazy('order_received', kwargs = {'ref_id': order_form.ref_id}))

        else:
            return render(request, 'order_create_new.html', {'baseorder_form': baseorder_form, 'customuser_form': customuser_form, 'customeruser_form': customeruser_form})


    def get(self, request, ref_id, uid = None):
        order = get_order_by_ref_id(ref_id)

        if not request.user.is_employee and not request.user.is_superuser and (request.user != order.customer.user):
            return HttpResponseRedirect(reverse_lazy('invalid'))

        customuser_form = None
        customeruser_form = None

        if request.user.is_employee or request.user.is_superuser:
            # if customer_uid:
            #     print("UID:", customer_uid)
            # if:
            customuser_form = UnregisteredUserForm(instance = order.customer.user, prefix='customuser_form')
            customeruser_form = UnregisteredCustomerForm(instance = order.customer, prefix='customeruser_form')

        baseorder_form = BaseOrderForm(instance = order, prefix="baseorder_form")
        return render(request, 'order_create_new.html', {
                                        'baseorder_form'   : baseorder_form,
                                        'customuser_form'  : customuser_form,
                                        'customeruser_form': customeruser_form,
                                        'customer_uuid_opt': uid,
                                        # 'existing_customer': True if customer_uid else False
                                    })


class OrderOptionView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_employee or request.user.is_superuser:
            return render(request, 'order_option.html')

        return HttpResponseRedirect(reverse_lazy('order_new'))



class CustomerSearchView(LoginRequiredMixin, ListView):
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

    def get(self, request):
        if request.user.is_customer:
            return HttpResponseRedirect(reverse_lazy('invalid'))
        return super(CustomerSearchView, self).get(self, request)

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
