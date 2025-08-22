from django.urls import path
from . import views

app_name = "home"
urlpatterns = [
    path('',views.home,name='home'),
    path("payment/",views.payment_gate, name="payment_gate"),
    path('payment/validation/',views.payment_validation,name="payment_validation"),
]

