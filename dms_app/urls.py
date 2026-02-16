from django.urls import path
from .views.auth import register_view, login_view
from .views.main import home_view

urlpatterns = [
    path("",home_view,name="home"),
    path("register/",register_view,name="register"),
    path("login/",login_view,name="login"),
]