"""Контекстный процессор для общих данных сайта."""
from django.conf import settings

from hospital.models import Department, News


def site_context(request):
    return {
        'site_name': settings.SITE_NAME,
        'site_name_short': settings.SITE_NAME_SHORT,
        'site_author': settings.SITE_AUTHOR,
        'site_address': settings.SITE_ADDRESS,
        'departments_menu': Department.objects.filter(is_active=True)[:8],
        'latest_news': News.objects.filter(is_published=True)[:3],
    }
