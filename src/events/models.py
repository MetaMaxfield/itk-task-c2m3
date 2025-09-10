import uuid

from django.db import models


class Location(models.Model):
    """Location model."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField("Название", max_length=50)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"


class Event(models.Model):
    """Event model."""

    OPEN_STATUS = "open"
    CLOSED_STATUS = "closed"
    STATUS_TYPES = [(OPEN_STATUS, "Открыт"), (CLOSED_STATUS, "Закрыт")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("Название", max_length=50)
    event_time = models.DateTimeField("Дата и время проведения мероприятия")
    registration_deadline = models.DateTimeField("Крайний срок регистрации")
    status = models.CharField("Текущий статус", choices=STATUS_TYPES)
    location = models.ForeignKey(
        "Location", blank=True, null=True, on_delete=models.SET_NULL
    )
    changed_at = models.DateTimeField("Дата и время изменения мероприятия")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
