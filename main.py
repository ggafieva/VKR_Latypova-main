#!/usr/bin/env python
"""
Точка входа для запуска веб-приложения ГАУЗ «Атнинская ЦРБ».

Использование:
    python main.py              — запуск сервера (http://127.0.0.1:8000)
    python main.py 8080         — запуск на другом порту
    python main.py migrate      — применить миграции
    python main.py load_initial_data — загрузить начальные данные
"""
import os
import sys


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crb_project.settings')

    from django.core.management import execute_from_command_line

    args = sys.argv[1:]
    if not args:
        execute_from_command_line(['manage.py', 'runserver'])
    elif args[0].isdigit():
        execute_from_command_line(['manage.py', 'runserver', args[0]])
    else:
        execute_from_command_line(['manage.py'] + args)


if __name__ == '__main__':
    main()
