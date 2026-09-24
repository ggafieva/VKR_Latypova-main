"""Management-команда начальной загрузки данных."""
from datetime import time

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from accounts.models import Role
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

User = get_user_model()


class Command(BaseCommand):
    help = 'Загрузка начальных данных для сайта Атнинской ЦРБ'

    def handle(self, *args, **options):
        self.stdout.write('Создание ролей...')
        roles = {}
        for code, name in Role.ROLE_CHOICES:
            role, _ = Role.objects.get_or_create(code=code, defaults={'name': name})
            roles[code] = role

        self.stdout.write('Создание пользователей...')
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@crb-atnya.ru',
                'first_name': 'Админ',
                'last_name': 'Системный',
                'is_staff': True,
                'is_superuser': True,
                'role': roles[Role.ADMIN],
            },
        )
        if created:
            admin_user.set_password('password123')
            admin_user.save()

        doctor_user, created = User.objects.get_or_create(
            username='doctor1',
            defaults={
                'email': 'doctor1@crb-atnya.ru',
                'first_name': 'Айрат',
                'last_name': 'Гарифуллин',
                'role': roles[Role.DOCTOR],
            },
        )
        if created:
            doctor_user.set_password('pass')
            doctor_user.save()

        patient_user, created = User.objects.get_or_create(
            username='patient1',
            defaults={
                'email': 'patient1@mail.ru',
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'phone': '+7 (843) 522-12-99',
                'role': roles[Role.PATIENT],
            },
        )
        if created:
            patient_user.set_password('pass')
            patient_user.save()

        self.stdout.write('Создание отделений...')
        departments_data = [
            ('terapevticheskoe', 'Терапевтическое отделение', 'Оказывает первичную медико-санитарную помощь взрослому населению.', '1', '+7 (843) 522-12-40', 0, 'Приём по записи и в порядке живой очереди.'),
            ('pediatricheskoe', 'Педиатрическое отделение', 'Медицинская помощь детям от 0 до 18 лет.', '2', '+7 (843) 522-12-41', 0, 'Детский кабинет, профилактические осмотры, вакцинация.'),
            ('hirurgicheskoe', 'Хирургическое отделение', 'Плановые и экстренные хирургические вмешательства.', '3', '+7 (843) 522-12-42', 15, 'Операционный блок, послеоперационное наблюдение.'),
            ('stacionar', 'Стационар', 'Круглосуточный стационар.', '2-3', '+7 (843) 522-12-43', 120, 'Круглосуточное наблюдение, палаты повышенного комфорта.'),
            ('laboratoriya', 'Клинико-диагностическая лаборатория', 'Лабораторные исследования и анализы.', '1', '+7 (843) 522-12-44', 0, 'Анализы крови, мочи, биохимия.'),
            ('rentgen', 'Рентгенологический кабинет', 'Рентгенография, флюорография, КТ.', '1', '+7 (843) 522-12-45', 0, 'Флюорография — по графику, КТ — по направлению.'),
        ]
        departments = {}
        for idx, (slug, name, desc, floor, phone, beds, extra) in enumerate(departments_data):
            dept, _ = Department.objects.update_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'description': desc,
                    'floor': floor,
                    'phone': phone,
                    'beds_count': beds,
                    'extra_info': extra,
                    'order': idx,
                },
            )
            departments[slug] = dept

        self.stdout.write('Создание руководства...')
        leaders = [
            ('Хафизов Ринат Равилевич', 'Главный врач', 'Высшее медицинское образование, стаж 25 лет. Организатор здравоохранения.'),
            ('Ахметова Лилия Минзакировна', 'Заместитель главного врача по медицинской части', 'Кандидат медицинских наук, врач-терапевт высшей категории.'),
            ('Сафин Ильдар Фаритович', 'Заместитель главного врача по экономике', 'Организация финансово-хозяйственной деятельности учреждения.'),
        ]
        for idx, (name, position, bio) in enumerate(leaders):
            Leadership.objects.get_or_create(
                full_name=name,
                defaults={'position': position, 'bio': bio, 'order': idx},
            )

        self.stdout.write('Создание врачей...')
        doctors_data = [
            ('garifullin-ajrat', 'Гарифуллин Айрат Рашитович', 'terapevticheskoe', 'Врач-терапевт', 'Высшая категория', 18, '101', doctor_user),
            ('safina-guzel', 'Сафина Гузель Маратовна', 'terapevticheskoe', 'Врач-терапевт', 'Первая категория', 12, '102', None),
            ('nurullin-rustem', 'Нуруллин Рустем Ильдарович', 'pediatricheskoe', 'Врач-педиатр', 'Высшая категория', 15, '201', None),
            ('hakimova-alina', 'Хакимова Алина Ринатовна', 'pediatricheskoe', 'Врач-педиатр', 'Вторая категория', 8, '202', None),
            ('valeev-marcel', 'Валеев Марсель Ринатович', 'hirurgicheskoe', 'Врач-хирург', 'Высшая категория', 20, '301', None),
            ('gimazova-liliya', 'Гимазова Лилия Фанисовна', 'laboratoriya', 'Врач-клинический лабораторный диагност', 'Первая категория', 10, '105', None),
        ]
        doctors = {}
        for slug, name, dept_slug, specialty, qual, exp, cabinet, user in doctors_data:
            doctor, _ = Doctor.objects.get_or_create(
                slug=slug,
                defaults={
                    'full_name': name,
                    'department': departments[dept_slug],
                    'specialty': specialty,
                    'qualification': qual,
                    'experience_years': exp,
                    'cabinet': cabinet,
                    'user': user,
                    'bio': f'{name} работает в Атнинской ЦРБ более {exp} лет. Специализируется на диагностике и лечении пациентов.',
                    'education': 'Казанский государственный медицинский университет',
                    'phone': f'+7 (843) 522-12-{cabinet[-2:]}',
                },
            )
            doctors[slug] = doctor

        self.stdout.write('Создание расписания...')
        schedule_data = [
            ('garifullin-ajrat', 0, '08:00', '14:00', '101'),
            ('garifullin-ajrat', 2, '08:00', '14:00', '101'),
            ('garifullin-ajrat', 4, '08:00', '12:00', '101'),
            ('safina-guzel', 1, '09:00', '15:00', '102'),
            ('safina-guzel', 3, '09:00', '15:00', '102'),
            ('nurullin-rustem', 0, '08:30', '13:30', '201'),
            ('nurullin-rustem', 2, '08:30', '13:30', '201'),
            ('nurullin-rustem', 4, '08:30', '12:30', '201'),
            ('hakimova-alina', 1, '10:00', '16:00', '202'),
            ('hakimova-alina', 3, '10:00', '16:00', '202'),
            ('valeev-marcel', 1, '08:00', '14:00', '301'),
            ('valeev-marcel', 3, '08:00', '14:00', '301'),
            ('valeev-marcel', 5, '09:00', '12:00', '301'),
        ]
        for doc_slug, day, start, end, room in schedule_data:
            Schedule.objects.get_or_create(
                doctor=doctors[doc_slug],
                day_of_week=day,
                start_time=time.fromisoformat(start),
                defaults={'end_time': time.fromisoformat(end), 'room': room},
            )

        self.stdout.write('Создание услуг...')
        services = [
            ('Приём терапевта', 'terapevticheskoe', 'Первичный и повторный приём врача-терапевта.'),
            ('Приём педиатра', 'pediatricheskoe', 'Консультация и осмотр ребёнка.'),
            ('Общий анализ крови', 'laboratoriya', 'Клинический анализ крови с лейкоцитарной формулой.'),
            ('Флюорография', 'rentgen', 'Рентгенологическое исследование органов грудной клетки.'),
            ('ЭКГ', 'terapevticheskoe', 'Электрокардиография в 12 отведениях.'),
            ('Хирургическая консультация', 'hirurgicheskoe', 'Осмотр и консультация хирурга.'),
        ]
        for name, dept_slug, desc in services:
            Service.objects.get_or_create(
                name=name,
                defaults={'department': departments[dept_slug], 'description': desc},
            )

        self.stdout.write('Создание новостей...')
        news_items = [
            ('vakcinaciya-detej', 'Вакцинация детей по календарю прививок', 'С 1 сентября в поликлинике проводится вакцинация детей согласно национальному календарю.'),
            ('novoe-oborudovanie', 'Новое диагностическое оборудование в лаборатории', 'Лаборатория оснащена современным автоматическим анализатором.'),
            ('den-zdorovya', 'День здоровья в Атнинском районе', 'Приглашаем жителей на профилактический осмотр 15 октября.'),
        ]
        for slug, title, content in news_items:
            News.objects.get_or_create(
                slug=slug,
                defaults={'title': title, 'content': content, 'excerpt': content[:100], 'author': admin_user},
            )

        self.stdout.write('Создание информации о больнице...')
        about_sections = [
            ('История', (
                'Государственное автономное учреждение здравоохранения '
                '«Атнинская центральная районная больница» (ГАУЗ) основано в 1952 году. '
                'За более чем 70 лет работы больница стала главным медицинским '
                'учреждением Атнинского района Республики Татарстан.'
            )),
            ('Миссия', 'Обеспечение доступной и качественной медицинской помощи жителям Атнинского района, внедрение современных методов диагностики и лечения.'),
            ('Структура', 'Больница включает поликлиническое отделение, стационар на 120 коек, дневной стационар, отделение скорой медицинской помощи, клинико-диагностическую лабораторию.'),
        ]
        for idx, (title, content) in enumerate(about_sections):
            HospitalInfo.objects.update_or_create(
                title=title,
                defaults={'content': content, 'section': 'about', 'order': idx},
            )

        self.stdout.write('Создание информации для пациентов...')
        patient_info = [
            ('podgotovka-k-analizam', 'Подготовка к анализам', 'Перед сдачей крови необходимо соблюдать голодание 8-12 часов. За сутки исключить алкоголь и жирную пищу.'),
            ('dokumenty-dlya-priema', 'Документы для приёма', 'Паспорт, полис ОМС, СНИЛС. Для детей — свидетельство о рождении и полис.'),
            ('prava-pacienta', 'Права пациента', 'Право на выбор врача, получение информации о состоянии здоровья, конфиденциальность медицинской информации.'),
            ('platnye-uslugi', 'Платные услуги', 'Перечень платных медицинских услуг утверждён приказом главного врача. Стоимость уточняйте в регистратуре.'),
        ]
        for idx, (slug, title, content) in enumerate(patient_info):
            PatientInfo.objects.get_or_create(
                slug=slug,
                defaults={'title': title, 'content': content, 'order': idx},
            )

        self.stdout.write('Создание тестовых заявок...')
        Feedback.objects.get_or_create(
            email='test@mail.ru',
            subject='Вопрос о записи',
            defaults={
                'name': 'Тестовый Пользователь',
                'phone': '+7 (843) 522-12-00',
                'message': 'Как записаться к терапевту через сайт?',
            },
        )

        self.stdout.write(self.style.SUCCESS('Начальные данные успешно загружены!'))
