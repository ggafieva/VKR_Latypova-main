"""Формы публичной части и личного кабинета."""
from django import forms
from django.db.models import Q

from accounts.models import CustomUser, Role
from hospital.models import Appointment, Department, Doctor, Feedback, PatientInfo, Schedule

class FeedbackForm(forms.ModelForm):
    captcha_answer = forms.IntegerField(
        label='Сколько будет 3 + 4?',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ответ'}),
    )

    class Meta:
        model = Feedback
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (___) ___-__-__'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Тема обращения'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Ваше сообщение'}),
        }

    def clean_captcha_answer(self):
        answer = self.cleaned_data.get('captcha_answer')
        if answer != 7:
            raise forms.ValidationError('Неверный ответ на проверочный вопрос.')
        return answer


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason']
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['day_of_week', 'start_time', 'end_time', 'room', 'notes']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.TextInput(attrs={'class': 'form-control'}),
        }


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = [
            'name', 'slug', 'description', 'phone', 'floor',
            'beds_count', 'extra_info', 'is_active', 'order',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (843) 522-12-__'}),
            'floor': forms.TextInput(attrs={'class': 'form-control'}),
            'beds_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'extra_info': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }


class DoctorAdminForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = [
            'department', 'full_name', 'slug', 'specialty', 'qualification',
            'experience_years', 'bio', 'education', 'phone', 'cabinet',
            'photo', 'user', 'is_active',
        ]
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'specialty': forms.TextInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'cabinet': forms.TextInput(attrs={'class': 'form-control'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.order_by('name')
        self.fields['user'].required = False
        self.fields['user'].empty_label = '— Без учётной записи —'
        self.fields['slug'].required = False
        doctor = self.instance if self.instance and self.instance.pk else None
        user_qs = CustomUser.objects.filter(role__code=Role.DOCTOR).order_by('username')
        if doctor:
            user_qs = user_qs.filter(Q(doctor_profile__isnull=True) | Q(doctor_profile=doctor))
        else:
            user_qs = user_qs.filter(doctor_profile__isnull=True)
        self.fields['user'].queryset = user_qs

    def clean_slug(self):
        from hospital.utils import slugify_name

        slug = self.cleaned_data.get('slug', '').strip()
        full_name = self.cleaned_data.get('full_name', '')
        if not slug and full_name:
            slug = slugify_name(full_name)
        if not slug:
            raise forms.ValidationError('Укажите URL (slug) или заполните ФИО для автогенерации.')
        return slug

    def save(self, commit=True):
        from hospital.utils import slugify_name

        doctor = super().save(commit=False)
        if not doctor.slug and doctor.full_name:
            doctor.slug = slugify_name(doctor.full_name)
        if commit:
            doctor.save()
            self.save_m2m()
        return doctor


class PatientInfoAdminForm(forms.ModelForm):
    class Meta:
        model = PatientInfo
        fields = ['title', 'slug', 'content', 'attachment', 'category', 'order', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Подготовка к анализам, Документы',
            }),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['category'].required = False
        self.fields['content'].required = False

    def clean(self):
        cleaned = super().clean()
        content = cleaned.get('content', '').strip()
        attachment = cleaned.get('attachment') or (
            self.instance.attachment if self.instance and self.instance.pk else None
        )
        if not content and not attachment:
            raise forms.ValidationError('Заполните текст или загрузите файл-памятку.')
        return cleaned

    def clean_slug(self):
        from hospital.utils import slugify_name

        slug = self.cleaned_data.get('slug', '').strip()
        title = self.cleaned_data.get('title', '')
        if not slug and title:
            slug = slugify_name(title)
        if not slug:
            raise forms.ValidationError('Укажите URL (slug) или заполните заголовок для автогенерации.')
        return slug

    def save(self, commit=True):
        from hospital.utils import slugify_name

        item = super().save(commit=False)
        if not item.slug and item.title:
            item.slug = slugify_name(item.title)
        if commit:
            item.save()
            self.save_m2m()
        return item
