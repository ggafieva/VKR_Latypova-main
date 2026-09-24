"""Модели пользователей и ролей."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """Роль пользователя в системе."""

    ADMIN = 'admin'
    DOCTOR = 'doctor'
    PATIENT = 'patient'

    ROLE_CHOICES = [
        (ADMIN, 'Администратор'),
        (DOCTOR, 'Врач'),
        (PATIENT, 'Пользователь/Пациент'),
    ]

    code = models.CharField('Код роли', max_length=20, choices=ROLE_CHOICES, unique=True)
    name = models.CharField('Название', max_length=100)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'
        ordering = ['code']

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """Расширенная модель пользователя."""

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        verbose_name='Роль',
        related_name='users',
        null=True,
        blank=True,
    )
    phone = models.CharField('Телефон', max_length=20, blank=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    address = models.CharField('Адрес', max_length=255, blank=True)
    email_notifications = models.BooleanField('Email-уведомления', default=True)
    sms_notifications = models.BooleanField('SMS-уведомления', default=False)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_admin_role(self):
        return self.role and self.role.code == Role.ADMIN

    @property
    def is_doctor_role(self):
        return self.role and self.role.code == Role.DOCTOR

    @property
    def is_patient_role(self):
        return self.role and self.role.code == Role.PATIENT
