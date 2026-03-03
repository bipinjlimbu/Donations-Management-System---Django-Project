from django.urls import path
from .views.auth import register_view, login_view, logout_view
from .views.main import home_view, contact_view, about_view, admin_dashboard_view, approve_signup_request, reject_signup_request, donate_view
from .views.profile import profile_view, edit_profile_view, approve_pending_changes, reject_profile_changes
from .views.campaigns import campaigns_page_view, create_campaign_view, edit_campaign_view, delete_campaign_view, approve_campaign_request, reject_campaign_request, single_campaign_page_view

urlpatterns = [
    path("",home_view,name="home"),
    path("contact/",contact_view,name="contact"),
    path("about/",about_view,name="about"),
    path("register/",register_view,name="register"),
    path("login/",login_view,name="login"),
    path("logout/",logout_view,name="logout"),
    path("profile/<int:user_id>/", profile_view, name="profile"),
    path("profile/edit/<int:user_id>/", edit_profile_view, name="edit-profile"),
    path("dashboard/admin/",admin_dashboard_view,name="admin-dashboard"),
    path("campaigns/",campaigns_page_view,name="campaigns"),
    path("campaigns/create/",create_campaign_view,name="create-campaign"),
    path("campaigns/edit/<int:campaign_id>/", edit_campaign_view, name="edit-campaign"),
    path("campaigns/delete/<int:campaign_id>/", delete_campaign_view, name="delete-campaign"),
    path("campaigns/<int:campaign_id>/", single_campaign_page_view, name="single-campaign"),
    path("campaigns/donate/<int:campaign_id>/", donate_view, name="donate"),
    path("approve_signup_request/<int:request_id>/", approve_signup_request, name="approve_signup_request"),
    path("reject_signup_request/<int:request_id>/", reject_signup_request, name="reject_signup_request"),
    path("approve_profile_change/<int:user_id>/", approve_pending_changes, name="approve_profile_change"),
    path("reject_profile_change/<int:user_id>/", reject_profile_changes, name="reject_profile_change"),
    path("approve_campaign_request/<int:campaign_id>/", approve_campaign_request, name="approve_campaign_request"),
    path("reject_campaign_request/<int:campaign_id>/", reject_campaign_request, name="reject_campaign_request"),
]