import re

from rest_framework import serializers


def validate_username(value):
    if value.lower() == 'me':
        raise serializers.ValidationError('Некорректное имя пользователя.')
    forbidden_chars = re.sub(r'[\w.@+-]', '', value)\

    unique_forbidden = ''.join(sorted(set(forbidden_chars),
                                      key=forbidden_chars.index))

    if unique_forbidden:
        raise serializers.ValidationError(
            'Имя пользователя может содержать только буквы, '
            'цифры и символы @/./+/-/_ \n'
            f'Вы использовали запрещённые символы: {unique_forbidden}'
        )
    return value


class UsernameValidationMixin:
    """Валидация username."""

    def validate_username(self, username):
        return validate_username(username)
