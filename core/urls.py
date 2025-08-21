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



    path('meters/', views.meters_list, name='meters'),  # All meters page
    path('meters/<int:meter_id>/', views.meter_detail, name='meter_detail'),  # Specific meter
    path("meters/add/", views.meter_add, name="meter_add"),
    path("meters/<int:meter_id>/edit/", views.meter_edit, name="meter_edit"),
    path("meters/<int:meter_id>/delete/", views.meter_delete, name="meter_delete"),

    # Categories
    path("water-management/", views.water_management, name="water_management"),
    path("billing-payments/", views.billing_payments, name="billing_payments"),
    path("reports-analysis/", views.reports_analysis, name="reports_analysis"),
    path("system-settings/", views.system_settings, name="system_settings"),

    # Authentication
    path("login/", LoginView.as_view(template_name="core/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]
