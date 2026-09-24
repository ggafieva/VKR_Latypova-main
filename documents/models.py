"""Модели сгенерированных документов."""
from django.conf import settings
from django.db import models


class GeneratedDocument(models.Model):
    """Запись о сгенерированном документе (docx/xlsx)."""

    TYPE_SCHEDULE = 'schedule_docx'
    TYPE_FEEDBACK_REPORT = 'feedback_xlsx'
    TYPE_APPOINTMENT = 'appointment_docx'

    TYPE_CHOICES = [
        (TYPE_SCHEDULE, 'Расписание врача (DOCX)'),
        (TYPE_FEEDBACK_REPORT, 'Отчёт по заявкам (XLSX)'),
        (TYPE_APPOINTMENT, 'Справка о записи (DOCX)'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_documents',
        verbose_name='Пользователь',
    )
    document_type = models.CharField('Тип документа', max_length=30, choices=TYPE_CHOICES)
    title = models.CharField('Название', max_length=255)
    parameters = models.JSONField('Параметры генерации', default=dict, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.get_document_type_display()})'
