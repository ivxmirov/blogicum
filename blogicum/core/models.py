from django.db import models


class BaseModel(models.Model):
    """
    Абстрактная модель. Добавляет флаг is_published и
    created_at - дату и время добавления публикации в базу данных
    """

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True
