from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from reviews.constants import (
    DISPLAY_LIMIT,
    MAX_LENGTH_FIELD_NAME,
    MAX_REVIEW_SCORE,
    MIN_REVIEW_SCORE,
)
from reviews.core import AbstractNameSlug, AbstractTextPubDateAuthor
from reviews.validators import year_validator


User = get_user_model()


class Category(AbstractNameSlug):
    """Модель категории произведения."""

    class Meta(AbstractNameSlug.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(AbstractNameSlug):
    """Модель жанра произведения."""

    class Meta(AbstractNameSlug.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    """Модель произведения."""

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='titles',
        verbose_name='Категория'
    )
    genres = models.ManyToManyField(Genre, verbose_name='Жанры')
    name = models.CharField(
        'Название произведения',
        max_length=MAX_LENGTH_FIELD_NAME
    )
    description = models.TextField('Описание', null=True, blank=True)
    year = models.SmallIntegerField(
        'Год выпуска',
        validators=(year_validator,)
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:DISPLAY_LIMIT]


class Review(AbstractTextPubDateAuthor):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(
            MinValueValidator(
                MIN_REVIEW_SCORE,
                f'Оценка не должна быть меньше {MIN_REVIEW_SCORE}'
            ),
            MaxValueValidator(
                MAX_REVIEW_SCORE,
                f'Оценка не должна быть больше {MAX_REVIEW_SCORE}'
            )
        )
    )

    class Meta(AbstractTextPubDateAuthor.Meta):
        default_related_name = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_review',
            ),
        )


class Comment(AbstractTextPubDateAuthor):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(AbstractTextPubDateAuthor.Meta):
        default_related_name = 'comments'
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
