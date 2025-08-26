# core/urls.py
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
        # Customers & Meters gateway
    path('customers-meters/', views.customers_meters, name='customers_meters'),
    path("customers/", views.customers, name="customers"),
    path("customers/<int:customer_id>/", views.customer_detail, name="customer_detail"),
    path('customers/<int:id>/edit/', views.customer_edit, name='customer_edit'),
    path('customers/<int:id>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/add/', views.customer_add, name='customer_add'),




    path("add-meter-reading/", views.add_meter_reading, name="add_meter_reading"),

    path('meters/', views.meters_list, name='meters'),  # All meters page
    path('meters/<int:meter_id>/', views.meter_detail, name='meter_detail'),  # Specific meter
    path("meters/add/", views.meter_add, name="meter_add"),
    path("meters/<int:meter_id>/edit/", views.meter_edit, name="meter_edit"),
    path("meters/<int:meter_id>/delete/", views.meter_delete, name="meter_delete"),


    #path("billing/", views.billing_payments, name="billing_paymentss"),  # Main billing page
    path("billing/add/", views.bill_add, name="bill_add"),
    path("billing/edit/<int:bill_id>/", views.bill_edit, name="bill_edit"),
    path("billing/delete/<int:bill_id>/", views.bill_delete, name="bill_delete"),

    # ------------------ PAYMENT URLS ------------------
    path("payment/add/", views.payment_add, name="payment_add"),
    path("payment/edit/<int:payment_id>/", views.payment_edit, name="payment_edit"),
    path("payment/delete/<int:payment_id>/", views.payment_delete, name="payment_delete"),


    # Categories
    path("water-management/", views.water_management, name="water_management"),

    path("reports-analysis/", views.reports_analysis, name="reports_analysis"),
    path("system-settings/", views.system_settings, name="system_settings"),


#real billing code here
    path("billing-payments/", views.billing_payments_gateway, name="billing_payments"),
    path("billing/", views.billing_list, name="billing_list"),
    path("payments/", views.payments_list, name="payments_list"),

    # Authentication
    path("login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
