"""Представления авторизации и личного кабинета."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required, doctor_required
from accounts.forms import LoginForm, NotificationSettingsForm, ProfileForm, RegisterForm
from accounts.models import Role
from documents.models import GeneratedDocument
from hospital.forms import AppointmentForm, ScheduleForm
from hospital.models import Appointment, Doctor, Feedback, Schedule


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, f'Добро пожаловать, {request.user.get_full_name() or request.user.username}!')
        next_url = request.GET.get('next', 'accounts:dashboard')
        return redirect(next_url)

    return render(request, 'accounts/login.html', {'form': form, 'page_title': 'Вход'})


def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('hospital:home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        patient_role = Role.objects.filter(code=Role.PATIENT).first()
        user.role = patient_role
        user.save()
        login(request, user)
        messages.success(request, 'Регистрация успешна! Добро пожаловать.')
        return redirect('accounts:dashboard')

    return render(request, 'accounts/register.html', {'form': form, 'page_title': 'Регистрация'})


@login_required
def dashboard(request):
    user = request.user
    context = {'page_title': 'Личный кабинет'}

    if user.is_admin_role:
        context.update({
            'appointments_count': Appointment.objects.count(),
            'feedbacks_count': Feedback.objects.filter(status=Feedback.STATUS_NEW).count(),
            'doctors_count': Doctor.objects.filter(is_active=True).count(),
        })
        template = 'accounts/dashboard_admin.html'
    elif user.is_doctor_role:
        doctor = getattr(user, 'doctor_profile', None)
        context['doctor'] = doctor
        if doctor:
            context['my_schedules'] = doctor.schedules.all()
            context['my_appointments'] = doctor.appointments.all()[:10]
        template = 'accounts/dashboard_doctor.html'
    else:
        context['my_appointments'] = user.appointments.all()[:5]
        context['my_feedbacks'] = user.feedbacks.all()[:5]
        template = 'accounts/dashboard_patient.html'

    return render(request, template, context)


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Профиль обновлён.')
        return redirect('accounts:profile')

    return render(request, 'accounts/profile.html', {
        'form': form,
        'page_title': 'Профиль',
        'breadcrumbs': [('Личный кабинет', 'accounts:dashboard'), ('Профиль', None)],
    })


@login_required
def my_appointments(request):
    user = request.user
    if user.is_doctor_role and hasattr(user, 'doctor_profile'):
        appointments = Appointment.objects.filter(doctor=user.doctor_profile)
    elif user.is_admin_role:
        appointments = Appointment.objects.all()
    else:
        appointments = user.appointments.all()

    return render(request, 'accounts/my_appointments.html', {
        'appointments': appointments,
        'page_title': 'Мои заявки к врачу',
        'breadcrumbs': [('Личный кабинет', 'accounts:dashboard'), ('Мои заявки', None)],
    })


@login_required
def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = request.user
        appointment.save()
        messages.success(request, 'Заявка на приём отправлена.')
        return redirect('accounts:my_appointments')

    return render(request, 'accounts/appointment_form.html', {
        'form': form,
        'page_title': 'Запись на приём',
        'breadcrumbs': [
            ('Личный кабинет', 'accounts:dashboard'),
            ('Запись на приём', None),
        ],
    })


@login_required
def document_history(request):
    documents = GeneratedDocument.objects.filter(user=request.user)
    return render(request, 'accounts/document_history.html', {
        'documents': documents,
        'page_title': 'История документов',
        'breadcrumbs': [('Личный кабинет', 'accounts:dashboard'), ('Документы', None)],
    })


@login_required
def notification_settings(request):
    form = NotificationSettingsForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Настройки уведомлений сохранены.')
        return redirect('accounts:notification_settings')

    return render(request, 'accounts/notification_settings.html', {
        'form': form,
        'page_title': 'Настройки уведомлений',
        'breadcrumbs': [('Личный кабинет', 'accounts:dashboard'), ('Уведомления', None)],
    })


@doctor_required
def doctor_schedule_manage(request):
    doctor = get_object_or_404(Doctor, user=request.user)
    schedules = doctor.schedules.all()

    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.doctor = doctor
            schedule.save()
            messages.success(request, 'Запись расписания добавлена.')
            return redirect('accounts:doctor_schedule')
    else:
        form = ScheduleForm()

    return render(request, 'accounts/doctor_schedule.html', {
        'form': form,
        'schedules': schedules,
        'doctor': doctor,
        'page_title': 'Моё расписание',
        'breadcrumbs': [('Личный кабинет', 'accounts:dashboard'), ('Расписание', None)],
    })


@doctor_required
def doctor_feedbacks(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'accounts/doctor_feedbacks.html', {
        'feedbacks': feedbacks,
        'page_title': 'Заявки обратной связи',
        'breadcrumbs': [('Личный кабинет', 'accounts:dashboard'), ('Заявки', None)],
    })


@doctor_required
def doctor_schedule_delete(request, pk):
    doctor = get_object_or_404(Doctor, user=request.user)
    schedule = get_object_or_404(Schedule, pk=pk, doctor=doctor)
    schedule.delete()
    messages.success(request, 'Запись расписания удалена.')
    return redirect('accounts:doctor_schedule')
