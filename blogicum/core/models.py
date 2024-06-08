from django.db import models


class BaseModel(models.Model):
    """
    Абстрактная модель. Добавляет поле
    created_at - дату и время добавления объекта в базу данных
    """

    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True
    )

    class Meta:
        abstract = True


class BaseModelPublished(BaseModel):
    """
    Абстрактная модель. Наследник модели BaseModel.
    Наследует поле created_at и добавляет флаг is_published
    """

    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )

    class Meta:
        abstract = True
