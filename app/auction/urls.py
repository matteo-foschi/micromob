from django.urls import path
from . import views

urlpatterns = [
    path("", views.homePage, name="homePage"),
    path("login", views.logIn, name="logIn"),
    path("register", views.register, name="register"),
]
