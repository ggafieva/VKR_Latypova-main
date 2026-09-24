"""Модели данных больницы."""
from django.conf import settings
from django.db import models


class Department(models.Model):
    """Отделение больницы."""

    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    floor = models.CharField('Этаж', max_length=10, blank=True)
    beds_count = models.PositiveIntegerField('Количество коек', default=0)
    extra_info = models.TextField('Дополнительная информация', blank=True)
    is_active = models.BooleanField('Активно', default=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Отделение'
        verbose_name_plural = 'Отделения'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Leadership(models.Model):
    """Руководство больницы."""

    full_name = models.CharField('ФИО', max_length=200)
    position = models.CharField('Должность', max_length=200)
    bio = models.TextField('Биография', blank=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    photo = models.ImageField('Фото', upload_to='leadership/', blank=True, null=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Руководитель'
        verbose_name_plural = 'Руководство'
        ordering = ['order']

    def __str__(self):
        return f'{self.full_name} — {self.position}'


class Doctor(models.Model):
    """Врач."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctor_profile',
        verbose_name='Учётная запись',
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='doctors',
        verbose_name='Отделение',
    )
    full_name = models.CharField('ФИО', max_length=200)
    slug = models.SlugField('URL', unique=True)
    specialty = models.CharField('Специальность', max_length=200)
    qualification = models.CharField('Квалификация', max_length=200, blank=True)
    experience_years = models.PositiveIntegerField('Стаж (лет)', default=0)
    bio = models.TextField('О враче')
    education = models.TextField('Образование', blank=True)
    photo = models.ImageField('Фото', upload_to='doctors/', blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    cabinet = models.CharField('Кабинет', max_length=20, blank=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Врач'
        verbose_name_plural = 'Врачи'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name


class Schedule(models.Model):
    """Расписание работы врача."""

    DAYS = [
        (0, 'Понедельник'),
        (1, 'Вторник'),
        (2, 'Среда'),
        (3, 'Четверг'),
        (4, 'Пятница'),
        (5, 'Суббота'),
        (6, 'Воскресенье'),
    ]

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='Врач',
    )
    day_of_week = models.IntegerField('День недели', choices=DAYS)
    start_time = models.TimeField('Начало приёма')
    end_time = models.TimeField('Конец приёма')
    room = models.CharField('Кабинет', max_length=20, blank=True)
    notes = models.CharField('Примечание', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписания'
        ordering = ['doctor', 'day_of_week', 'start_time']
        unique_together = [['doctor', 'day_of_week', 'start_time']]

    def __str__(self):
        return f'{self.doctor} — {self.get_day_of_week_display()} {self.start_time}-{self.end_time}'


class Service(models.Model):
    """Медицинская услуга."""

    name = models.CharField('Название', max_length=200)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services',
        verbose_name='Отделение',
    )
    description = models.TextField('Описание')
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['name']

    def __str__(self):
        return self.name


class News(models.Model):
    """Новость или статья."""

    title = models.CharField('Заголовок', max_length=255)
    slug = models.SlugField('URL', unique=True)
    content = models.TextField('Содержание')
    excerpt = models.TextField('Краткое описание', blank=True)
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Автор',
    )
    is_published = models.BooleanField('Опубликовано', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Feedback(models.Model):
    """Заявка обратной связи."""

    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_DONE = 'done'

    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        (STATUS_IN_PROGRESS, 'В обработке'),
        (STATUS_DONE, 'Завершена'),
    ]

    name = models.CharField('Имя', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    subject = models.CharField('Тема', max_length=200)
    message = models.TextField('Сообщение')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks',
        verbose_name='Пользователь',
    )
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField('Дата', auto_now_add=True)
    admin_comment = models.TextField('Комментарий администратора', blank=True)

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} — {self.name}'


class UploadedFile(models.Model):
    """Файл, прикреплённый к объектам системы."""

    title = models.CharField('Название', max_length=200)
    file = models.FileField('Файл', upload_to='uploads/%Y/%m/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Загрузил',
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='files',
        verbose_name='Врач',
    )
    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='files',
        verbose_name='Новость',
    )
    feedback = models.ForeignKey(
        Feedback,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='files',
        verbose_name='Заявка',
    )
    patient_info = models.ForeignKey(
        'PatientInfo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='extra_files',
        verbose_name='Материал для пациентов',
    )
    uploaded_at = models.DateTimeField('Дата загрузки', auto_now_add=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Файл'
        verbose_name_plural = 'Файлы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class Appointment(models.Model):
    """Запись пациента на приём."""

    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Ожидает'),
        (STATUS_CONFIRMED, 'Подтверждена'),
        (STATUS_CANCELLED, 'Отменена'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Пациент',
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name='Врач',
    )
    appointment_date = models.DateField('Дата приёма')
    appointment_time = models.TimeField('Время приёма')
    reason = models.TextField('Причина обращения')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField('Создана', auto_now_add=True)
    notes = models.TextField('Примечания', blank=True)

    class Meta:
        verbose_name = 'Запись на приём'
        verbose_name_plural = 'Записи на приём'
        ordering = ['-appointment_date', '-appointment_time']

    def __str__(self):
        return f'{self.patient} → {self.doctor} ({self.appointment_date})'


class PatientInfo(models.Model):
    """Полезная информация для пациентов."""

    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('URL', unique=True)
    content = models.TextField('Содержание', blank=True)
    attachment = models.FileField(
        'Файл-памятка',
        upload_to='patient_memos/%Y/%m/',
        blank=True,
        null=True,
    )
    category = models.CharField('Категория', max_length=100, blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активно', default=True)

    class Meta:
        verbose_name = 'Информация для пациентов'
        verbose_name_plural = 'Информация для пациентов'
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    @property
    def has_attachment(self):
        return bool(self.attachment)

    @property
    def file_extension(self):
        if not self.attachment:
            return ''
        return self.attachment.name.rsplit('.', 1)[-1].lower()


class HospitalInfo(models.Model):
    """Общая информация о больнице (история, миссия)."""

    title = models.CharField('Заголовок', max_length=200)
    content = models.TextField('Содержание')
    section = models.CharField('Раздел', max_length=50, default='about')
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Информация о больнице'
        verbose_name_plural = 'Информация о больнице'
        ordering = ['order']

    def __str__(self):
        return self.title
