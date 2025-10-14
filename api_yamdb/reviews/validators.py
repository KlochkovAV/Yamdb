from django.core.exceptions import ValidationError
from django.utils import timezone


def year_validator(value):
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска не может быть больше текущего ({current_year}).'
        )
