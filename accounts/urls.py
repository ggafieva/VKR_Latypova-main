"""URL-маршруты авторизации и личного кабинета."""
from django.urls import path

from accounts import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('appointments/', views.my_appointments, name='my_appointments'),
    path('appointments/new/', views.appointment_create, name='appointment_create'),
    path('documents/', views.document_history, name='document_history'),
    path('notifications/', views.notification_settings, name='notification_settings'),
    path('doctor/schedule/', views.doctor_schedule_manage, name='doctor_schedule'),
    path('doctor/schedule/<int:pk>/delete/', views.doctor_schedule_delete, name='doctor_schedule_delete'),
    path('doctor/feedbacks/', views.doctor_feedbacks, name='doctor_feedbacks'),
]
