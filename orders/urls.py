from django.urls import path
from django.views.generic.base import TemplateView

from .views import (OrderListView,
                    OrderCreateView,
                    OrderOptionView,
                    CustomerSearchView,
                    ReceivedOrderView,
                    OrderDetailView,
                    OrderEditView)

urlpatterns = [
               path("", OrderListView.as_view(), name="order_view"),
               path("new", OrderCreateView.as_view(), name="order_new"),
               path('option', OrderOptionView.as_view(), name="order_option"),
               path("search_customer", CustomerSearchView.as_view(), name="search_customer"),
               path('order_exp', TemplateView.as_view(template_name="myOrderList.html"), name="exp"),
               path('order_received/<str:ref_id>', ReceivedOrderView.as_view(), name="order_received"),
               path('<str:ref_id>', OrderDetailView.as_view(), name="order_detail"),
               path('edit/<str:ref_id>', OrderEditView.as_view(), name="order_edit")
]
