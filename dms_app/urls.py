from django.urls import path
from .views.auth import register_view, login_view, logout_view
from .views.main import home_view, contact_view, about_view
from .views.admin_dashboard import admin_dashboard_view, approve_signup_request, reject_signup_request, mark_feedback_toggle, delete_feedback_view
from .views.donor_dashboard import donor_dashboard_view, donate_view
from .views.ngo_dashboard import ngo_dashboard_view, approve_donation_view, reject_donation_view
from .views.profile import profile_view, edit_profile_view, approve_profile_changes, reject_profile_changes
from .views.campaigns import campaigns_page_view, create_campaign_view, edit_campaign_view, delete_campaign_view, approve_campaign_request, reject_campaign_request, single_campaign_page_view
from .views.testimonials import testimonials_view, create_testimonial_view, approve_testimonial_view, reject_testimonial_view, edit_testimonial_view

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
    path("dashboard/ngo/",ngo_dashboard_view,name="ngo-dashboard"),
    path("dashboard/donor/",donor_dashboard_view,name="donor-dashboard"),
    path("campaigns/",campaigns_page_view,name="campaigns"),
    path("campaigns/create/",create_campaign_view,name="create-campaign"),
    path("campaigns/edit/<int:campaign_id>/", edit_campaign_view, name="edit-campaign"),
    path("campaigns/delete/<int:campaign_id>/", delete_campaign_view, name="delete-campaign"),
    path("campaigns/<int:campaign_id>/", single_campaign_page_view, name="single-campaign"),
    path("campaigns/donate/<int:campaign_id>/", donate_view, name="donate"),
    path("testimonials/", testimonials_view, name="testimonials"),
    path("testimonials/create/", create_testimonial_view, name="create-testimonial"),
    path("testimonials/edit/<int:testimonial_id>/", edit_testimonial_view, name="edit-testimonial"),
    path("approve_donation_request/<int:donation_id>/", approve_donation_view, name="approve_donation"),
    path("reject_donation_request/<int:donation_id>/", reject_donation_view, name="reject_donation"),
    path("approve_signup_request/<int:request_id>/", approve_signup_request, name="approve_signup_request"),
    path("reject_signup_request/<int:request_id>/", reject_signup_request, name="reject_signup_request"),
    path("mark_feedback_toggle/<int:feedback_id>/", mark_feedback_toggle, name="mark_feedback_toggle"),
    path("delete_feedback/<int:feedback_id>/", delete_feedback_view, name="delete_feedback"),
    path("approve_profile_change/<int:user_id>/", approve_profile_changes, name="approve_profile_change"),
    path("reject_profile_change/<int:user_id>/", reject_profile_changes, name="reject_profile_change"),
    path("approve_campaign_request/<int:campaign_id>/", approve_campaign_request, name="approve_campaign_request"),
    path("reject_campaign_request/<int:campaign_id>/", reject_campaign_request, name="reject_campaign_request"),
    path("approve_testimonial/<int:testimonial_id>/", approve_testimonial_view, name="approve_testimonial"),
    path("reject_testimonial/<int:testimonial_id>/", reject_testimonial_view, name="reject_testimonial"),
]