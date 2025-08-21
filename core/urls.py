from django.urls import path
from .views import dashboard, UserLoginView, UserLogoutView

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("", dashboard, name="dashboard"),  # Default homepage = dashboard
]
