from django.urls import path
from .views.auth import register_view, login_view, logout_view
from .views.main import home_view, admin_dashboard_view, approve_signup_request, reject_signup_request

urlpatterns = [
    path("",home_view,name="home"),
    path("register/",register_view,name="register"),
    path("login/",login_view,name="login"),
    path("logout/",logout_view,name="logout"),
    path("dashboard/admin/",admin_dashboard_view,name="admin-dashboard"),
    path("approve_signup_request/<int:request_id>/", approve_signup_request, name="approve_signup_request"),
    path("reject_signup_request/<int:request_id>/", reject_signup_request, name="reject_signup_request"),
]