from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("", views.homePage, name="homePage"),
    path("login", views.logIn, name="logIn"),
    path("register", views.register, name="register"),
    path("logout", views.logOut, name="logOut"),
]
