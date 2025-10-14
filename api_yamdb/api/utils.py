import random

from django.conf import settings
from django.core.mail import send_mail


def send_code_email(email, code):
    """Функция для отправки кода подтверждения на почту."""

    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [email]
    )


def generate_confirmation_code():
    """Функция для генерации кода подтверждения."""

    return ''.join(random.choices('0123456789', k=6))
