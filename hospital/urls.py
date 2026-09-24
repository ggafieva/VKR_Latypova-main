"""URL-маршруты публичной части."""
from django.urls import path

from hospital import views

app_name = 'hospital'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('leadership/', views.leadership, name='leadership'),
    path('departments/', views.departments_list, name='departments'),
    path('departments/<slug:slug>/', views.department_detail, name='department_detail'),
    path('doctors/', views.doctors_list, name='doctors'),
    path('doctors/<slug:slug>/', views.doctor_detail, name='doctor_detail'),
    path('patients/', views.patients_info, name='patients'),
    path('patients/<slug:slug>/', views.patient_info_detail, name='patient_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('feedback/', views.feedback_page, name='feedback'),
    path('feedback/thanks/', views.feedback_thanks, name='feedback_thanks'),
    path('schedule/', views.schedule_page, name='schedule'),
    path('news/', views.news_list, name='news'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
    path('services/', views.services_list, name='services'),
]
