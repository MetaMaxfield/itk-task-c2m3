from django.core.validators import MinValueValidator
from django.db import models


class SyncResult(models.Model):
    created_at = models.DateTimeField("Дата и время синхронизации", auto_now_add=True)
    added_count = models.IntegerField(
        "Количество новых добавленных мероприятий",
        validators=[
            MinValueValidator(0),
        ],
    )
    updated_count = models.IntegerField(
        "Количество обновленных мероприятий",
        validators=[
            MinValueValidator(0),
        ],
    )

    def __str__(self):
        return f"Синхронизация от {self.created_at}"

    class Meta:
        verbose_name = "Результат синхронизации"
        verbose_name_plural = "Результаты синхронизаций"
