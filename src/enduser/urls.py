from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import PasswordsChangeView
urlpatterns = [
    path('register/', views.registerPage, name = 'register'),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    path('login/',views.loginPage, name = 'login'),
    path('logout/',views.logoutPage, name = 'logout'),
    path('profile/', views.updateProfile, name='profile'),
    path('reset_password/',
            auth_views.PasswordResetView.as_view(template_name="enduser/password_reset.html"),
            name="password_reset"),
    path('reset_password_sent/', 
            auth_views.PasswordResetDoneView.as_view(template_name="enduser/password_reset_sent.html"), 
            name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
            auth_views.PasswordResetConfirmView.as_view(template_name="enduser/password_reset_form.html"), 
            name="password_reset_confirm"),
    path('reset_password_complete/', 
            auth_views.PasswordResetCompleteView.as_view(template_name="enduser/password_reset_done.html"), 
            name="password_reset_complete"),
    path('password/', PasswordsChangeView.as_view(template_name = "enduser/change_password.html"),name='password'),

    path('all_submissions/',views.allSubmissionPage,name='all_submissions'),
    path('submission/<int:submission_id>/', views.submission, name='submission'),
]