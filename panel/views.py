"""Кастомная панель администратора."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import admin_required
from accounts.models import CustomUser, Role
from documents.generators import DocumentGenerator
from hospital.models import Doctor, Department, Feedback, PatientInfo, Schedule, UploadedFile


@admin_required
def panel_dashboard(request):
    stats = {
        'doctors': Doctor.objects.count(),
        'departments': Department.objects.count(),
        'users': CustomUser.objects.count(),
        'feedbacks': Feedback.objects.filter(status=Feedback.STATUS_NEW).count(),
        'files': UploadedFile.objects.count(),
    }
    return render(request, 'panel/dashboard.html', {
        'stats': stats,
        'page_title': 'Панель администратора',
    })


@admin_required
def manage_doctors(request):
    doctors = Doctor.objects.select_related('department', 'user').order_by('department__name', 'full_name')
    if request.method == 'POST':
        action = request.POST.get('action')
        doctor_id = request.POST.get('doctor_id')
        if action == 'toggle' and doctor_id:
            doctor = get_object_or_404(Doctor, pk=doctor_id)
            doctor.is_active = not doctor.is_active
            doctor.save()
            messages.success(request, f'Статус врача {doctor.full_name} изменён.')
            return redirect('panel:doctors')

    return render(request, 'panel/doctors.html', {
        'doctors': doctors,
        'page_title': 'Управление врачами',
    })


@admin_required
def doctor_edit(request, pk=None):
    from hospital.forms import DoctorAdminForm

    doctor = get_object_or_404(Doctor, pk=pk) if pk else None
    form = DoctorAdminForm(request.POST or None, request.FILES or None, instance=doctor)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Врач «{form.instance.full_name}» сохранён.')
        return redirect('panel:doctors')

    title = f'Редактирование: {doctor.full_name}' if doctor else 'Добавить врача'
    return render(request, 'panel/doctor_edit.html', {
        'form': form,
        'doctor': doctor,
        'page_title': title,
    })


@admin_required
def manage_schedules(request):
    schedules = Schedule.objects.select_related('doctor', 'doctor__department').all()
    doctors = Doctor.objects.filter(is_active=True)
    return render(request, 'panel/schedules.html', {
        'schedules': schedules,
        'doctors': doctors,
        'page_title': 'Управление расписанием',
    })


@admin_required
def download_schedule_docx(request, doctor_id):
    doctor = get_object_or_404(Doctor, pk=doctor_id)
    buffer, filename = DocumentGenerator.generate_doctor_schedule_docx(doctor, request.user)
    from django.http import HttpResponse
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@admin_required
def manage_users(request):
    users = CustomUser.objects.select_related('role').all()
    roles = Role.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role_id = request.POST.get('role_id')
        if user_id and role_id:
            user = get_object_or_404(CustomUser, pk=user_id)
            user.role = get_object_or_404(Role, pk=role_id)
            user.save()
            messages.success(request, f'Роль пользователя {user.username} обновлена.')

    return render(request, 'panel/users.html', {
        'users': users,
        'roles': roles,
        'page_title': 'Управление пользователями',
    })


@admin_required
def manage_feedbacks(request):
    feedbacks = Feedback.objects.all()
    status_choices = Feedback.STATUS_CHOICES
    if request.method == 'POST':
        feedback_id = request.POST.get('feedback_id')
        new_status = request.POST.get('status')
        comment = request.POST.get('admin_comment', '')
        if feedback_id and new_status:
            feedback = get_object_or_404(Feedback, pk=feedback_id)
            feedback.status = new_status
            feedback.admin_comment = comment
            feedback.save()
            messages.success(request, 'Статус заявки обновлён.')

    return render(request, 'panel/feedbacks.html', {
        'feedbacks': feedbacks,
        'status_choices': status_choices,
        'page_title': 'Заявки обратной связи',
    })


@admin_required
def download_feedback_report(request):
    date_from = request.GET.get('date_from') or None
    date_to = request.GET.get('date_to') or None
    buffer, filename = DocumentGenerator.generate_feedback_report_xlsx(
        request.user, date_from=date_from, date_to=date_to
    )
    from django.http import HttpResponse
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@admin_required
def manage_files(request):
    files = UploadedFile.objects.select_related('uploaded_by', 'doctor', 'news').all()

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'upload':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '')
            uploaded_file = request.FILES.get('file')
            doctor_id = request.POST.get('doctor_id') or None
            if title and uploaded_file:
                file_obj = UploadedFile(
                    title=title,
                    file=uploaded_file,
                    description=description,
                    uploaded_by=request.user,
                )
                if doctor_id:
                    file_obj.doctor = get_object_or_404(Doctor, pk=doctor_id)
                file_obj.save()
                messages.success(request, 'Файл загружен.')
            else:
                messages.error(request, 'Укажите название и выберите файл.')
        elif action == 'delete':
            file_id = request.POST.get('file_id')
            if file_id:
                file_obj = get_object_or_404(UploadedFile, pk=file_id)
                file_obj.file.delete(save=False)
                file_obj.delete()
                messages.success(request, 'Файл удалён.')

    doctors = Doctor.objects.filter(is_active=True)
    return render(request, 'panel/files.html', {
        'files': files,
        'doctors': doctors,
        'page_title': 'Управление файлами',
    })


@admin_required
def manage_departments(request):
    departments = Department.objects.all()
    return render(request, 'panel/departments.html', {
        'departments': departments,
        'page_title': 'Состав больницы',
    })


@admin_required
def department_edit(request, pk=None):
    from hospital.forms import DepartmentForm

    department = get_object_or_404(Department, pk=pk) if pk else None
    form = DepartmentForm(request.POST or None, instance=department)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Отделение «{form.instance.name}» сохранено.')
        return redirect('panel:departments')

    title = f'Редактирование: {department.name}' if department else 'Новое отделение'
    return render(request, 'panel/department_edit.html', {
        'form': form,
        'department': department,
        'page_title': title,
    })


@admin_required
def department_toggle(request, pk):
    department = get_object_or_404(Department, pk=pk)
    department.is_active = not department.is_active
    department.save()
    status = 'активировано' if department.is_active else 'скрыто'
    messages.success(request, f'Отделение «{department.name}» {status}.')
    return redirect('panel:departments')


@admin_required
def manage_patient_info(request):
    items = PatientInfo.objects.all()
    return render(request, 'panel/patient_info.html', {
        'items': items,
        'page_title': 'Информация для пациентов',
    })


@admin_required
def patient_info_edit(request, pk=None):
    from hospital.forms import PatientInfoAdminForm

    item = get_object_or_404(PatientInfo, pk=pk) if pk else None
    form = PatientInfoAdminForm(request.POST or None, request.FILES or None, instance=item)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Материал «{form.instance.title}» сохранён.')
        return redirect('panel:patient_info')

    title = f'Редактирование: {item.title}' if item else 'Добавить материал'
    return render(request, 'panel/patient_info_edit.html', {
        'form': form,
        'item': item,
        'page_title': title,
    })


@admin_required
def patient_info_delete(request, pk):
    item = get_object_or_404(PatientInfo, pk=pk)
    if request.method == 'POST':
        title = item.title
        item.delete()
        messages.success(request, f'Материал «{title}» удалён.')
        return redirect('panel:patient_info')
    return render(request, 'panel/patient_info_delete.html', {
        'item': item,
        'page_title': 'Удаление материала',
    })


@admin_required
def patient_info_toggle(request, pk):
    item = get_object_or_404(PatientInfo, pk=pk)
    item.is_active = not item.is_active
    item.save()
    status = 'опубликован' if item.is_active else 'скрыт'
    messages.success(request, f'Материал «{item.title}» {status}.')
    return redirect('panel:patient_info')
