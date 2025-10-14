from django.contrib.auth import get_user_model
from django.db import models

from reviews.constants import (
    DISPLAY_LIMIT,
    MAX_LENGTH_FIELD_NAME,
    MAX_LENGTH_FIELD_SLUG,
)


User = get_user_model()


class AbstractNameSlug(models.Model):
    """Абстрактная модель для имени и slug."""

    name = models.CharField('Наименование', max_length=MAX_LENGTH_FIELD_NAME)
    slug = models.SlugField(
        'Slug',
        max_length=MAX_LENGTH_FIELD_SLUG,
        unique=True,
    )

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.name[:DISPLAY_LIMIT]


class AbstractTextPubDateAuthor(models.Model):
    """Абстрактная модель для текста, даты публикации и автора."""

    text = models.TextField('Текст', blank=False)
    pub_date = models.DateTimeField('Добавлен', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:DISPLAY_LIMIT]
