from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from api.validations import validate_username
from reviews.constants import (
    ADMIN,
    DISPLAY_LIMIT,
    MAX_BIO_LENGHT,
    MAX_CODE_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_NAME_LENGTH,
    MODERATOR,
    USER,
)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    class Role(models.TextChoices):
        USER = USER, _('Пользователь')
        MODERATOR = MODERATOR, _('Модератор')
        ADMIN = ADMIN, _('Администратор')

    role = models.CharField(
        'Роль',
        max_length=max(len(choice) for choice, _ in Role.choices),
        choices=Role.choices,
        default=Role.USER
    )
    email = models.EmailField(
        'Почта',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_NAME_LENGTH,
        blank=True,
        null=True
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=MAX_CODE_LENGTH,
        blank=True,
        null=True
    )
    bio = models.CharField(
        'Информация',
        max_length=MAX_BIO_LENGHT,
        blank=True,
        null=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=MAX_NAME_LENGTH,
        unique=True,
        validators=(validate_username,)
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return self.username[:DISPLAY_LIMIT]
