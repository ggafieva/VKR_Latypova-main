"""Публичные представления сайта больницы."""
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from hospital.forms import FeedbackForm
from hospital.models import (
    Department,
    Doctor,
    Feedback,
    HospitalInfo,
    Leadership,
    News,
    PatientInfo,
    Schedule,
    Service,
)


def home(request):
    doctors = Doctor.objects.filter(is_active=True).select_related('department')[:6]
    news_list = News.objects.filter(is_published=True)[:4]
    departments = Department.objects.filter(is_active=True)[:6]
    services = Service.objects.filter(is_active=True)[:6]
    context = {
        'doctors': doctors,
        'news_list': news_list,
        'departments': departments,
        'services': services,
        'page_title': 'Главная',
    }
    return render(request, 'hospital/home.html', context)


def about(request):
    sections = HospitalInfo.objects.all()
    context = {
        'sections': sections,
        'page_title': 'О больнице',
        'breadcrumbs': [('Главная', 'hospital:home'), ('О больнице', None)],
    }
    return render(request, 'hospital/about.html', context)


def leadership(request):
    leaders = Leadership.objects.all()
    context = {
        'leaders': leaders,
        'page_title': 'Руководство',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Руководство', None)],
    }
    return render(request, 'hospital/leadership.html', context)


def departments_list(request):
    departments = Department.objects.filter(is_active=True)
    context = {
        'departments': departments,
        'page_title': 'Отделения и службы',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Отделения и службы', None)],
    }
    return render(request, 'hospital/departments.html', context)


def department_detail(request, slug):
    department = get_object_or_404(Department, slug=slug, is_active=True)
    doctors = department.doctors.filter(is_active=True)
    services = department.services.filter(is_active=True)
    context = {
        'department': department,
        'doctors': doctors,
        'services': services,
        'page_title': department.name,
        'breadcrumbs': [
            ('Главная', 'hospital:home'),
            ('Отделения', 'hospital:departments'),
            (department.name, None),
        ],
    }
    return render(request, 'hospital/department_detail.html', context)


def doctors_list(request):
    doctors = Doctor.objects.filter(is_active=True).select_related('department')
    department_slug = request.GET.get('department')
    if department_slug:
        doctors = doctors.filter(department__slug=department_slug)
    departments = Department.objects.filter(is_active=True)
    context = {
        'doctors': doctors,
        'departments': departments,
        'selected_department': department_slug,
        'page_title': 'Врачи',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Врачи', None)],
    }
    return render(request, 'hospital/doctors.html', context)


def doctor_detail(request, slug):
    doctor = get_object_or_404(Doctor, slug=slug, is_active=True)
    schedules = doctor.schedules.all()
    files = doctor.files.all()
    context = {
        'doctor': doctor,
        'schedules': schedules,
        'files': files,
        'page_title': doctor.full_name,
        'breadcrumbs': [
            ('Главная', 'hospital:home'),
            ('Врачи', 'hospital:doctors'),
            (doctor.full_name, None),
        ],
    }
    return render(request, 'hospital/doctor_detail.html', context)


def patients_info(request):
    info_items = PatientInfo.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    context = {
        'info_items': info_items,
        'services': services,
        'page_title': 'Пациентам',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Пациентам', None)],
    }
    return render(request, 'hospital/patients.html', context)


def patient_info_detail(request, slug):
    item = get_object_or_404(PatientInfo, slug=slug, is_active=True)
    context = {
        'item': item,
        'info_items': PatientInfo.objects.filter(is_active=True),
        'page_title': item.title,
        'breadcrumbs': [
            ('Главная', 'hospital:home'),
            ('Пациентам', 'hospital:patients'),
            (item.title, None),
        ],
    }
    return render(request, 'hospital/patient_detail.html', context)


def contacts(request):
    context = {
        'page_title': 'Контакты',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Контакты', None)],
    }
    return render(request, 'hospital/contacts.html', context)


def feedback_page(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            send_mail(
                subject=f'[ЦРБ] Обратная связь: {feedback.subject}',
                message=(
                    f'Имя: {feedback.name}\n'
                    f'Email: {feedback.email}\n'
                    f'Телефон: {feedback.phone}\n\n'
                    f'{feedback.message}'
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.ADMIN_EMAIL],
                fail_silently=True,
            )
            return redirect('hospital:feedback_thanks')
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'phone': request.user.phone,
            }
        form = FeedbackForm(initial=initial)

    context = {
        'form': form,
        'page_title': 'Обратная связь',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Обратная связь', None)],
    }
    return render(request, 'hospital/feedback.html', context)


def feedback_thanks(request):
    context = {
        'page_title': 'Спасибо за обращение',
        'breadcrumbs': [
            ('Главная', 'hospital:home'),
            ('Обратная связь', 'hospital:feedback'),
            ('Спасибо', None),
        ],
    }
    return render(request, 'hospital/feedback_thanks.html', context)


def schedule_page(request):
    schedules = Schedule.objects.select_related('doctor', 'doctor__department').order_by(
        'doctor__full_name', 'day_of_week', 'start_time'
    )
    doctors = Doctor.objects.filter(is_active=True).prefetch_related('schedules')
    context = {
        'schedules': schedules,
        'doctors': doctors,
        'page_title': 'Расписание специалистов',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Расписание', None)],
    }
    return render(request, 'hospital/schedule.html', context)


def news_list(request):
    news_items = News.objects.filter(is_published=True)
    context = {
        'news_items': news_items,
        'page_title': 'Новости',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Новости', None)],
    }
    return render(request, 'hospital/news_list.html', context)


def news_detail(request, slug):
    article = get_object_or_404(News, slug=slug, is_published=True)
    context = {
        'article': article,
        'page_title': article.title,
        'breadcrumbs': [
            ('Главная', 'hospital:home'),
            ('Новости', 'hospital:news'),
            (article.title, None),
        ],
    }
    return render(request, 'hospital/news_detail.html', context)


def services_list(request):
    services = Service.objects.filter(is_active=True).select_related('department')
    context = {
        'services': services,
        'page_title': 'Услуги',
        'breadcrumbs': [('Главная', 'hospital:home'), ('Услуги', None)],
    }
    return render(request, 'hospital/services.html', context)
