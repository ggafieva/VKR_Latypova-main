"""URL-маршруты панели администратора."""
from django.urls import path

from panel import views

app_name = 'panel'

urlpatterns = [
    path('', views.panel_dashboard, name='dashboard'),
    path('departments/', views.manage_departments, name='departments'),
    path('departments/new/', views.department_edit, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/toggle/', views.department_toggle, name='department_toggle'),
    path('doctors/', views.manage_doctors, name='doctors'),
    path('doctors/new/', views.doctor_edit, name='doctor_create'),
    path('doctors/<int:pk>/edit/', views.doctor_edit, name='doctor_edit'),
    path('schedules/', views.manage_schedules, name='schedules'),
    path('schedules/<int:doctor_id>/docx/', views.download_schedule_docx, name='schedule_docx'),
    path('users/', views.manage_users, name='users'),
    path('feedbacks/', views.manage_feedbacks, name='feedbacks'),
    path('feedbacks/report/', views.download_feedback_report, name='feedback_report'),
    path('files/', views.manage_files, name='files'),
    path('patient-info/', views.manage_patient_info, name='patient_info'),
    path('patient-info/new/', views.patient_info_edit, name='patient_info_create'),
    path('patient-info/<int:pk>/edit/', views.patient_info_edit, name='patient_info_edit'),
    path('patient-info/<int:pk>/delete/', views.patient_info_delete, name='patient_info_delete'),
    path('patient-info/<int:pk>/toggle/', views.patient_info_toggle, name='patient_info_toggle'),
]
