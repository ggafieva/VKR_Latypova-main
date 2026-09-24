"""Декораторы проверки ролей."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def role_required(*role_codes):
    """Доступ только для указанных ролей."""

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.role or user.role.code not in role_codes:
                raise PermissionDenied('Недостаточно прав для доступа к этой странице.')
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def admin_required(view_func):
    """Доступ только для администратора."""
    from accounts.models import Role
    return role_required(Role.ADMIN)(view_func)


def doctor_required(view_func):
    """Доступ для врача или администратора."""
    from accounts.models import Role

    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user = request.user
        if not user.role or user.role.code not in (Role.DOCTOR, Role.ADMIN):
            raise PermissionDenied('Доступ только для врачей.')
        return view_func(request, *args, **kwargs)

    return wrapper
