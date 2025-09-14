from django.db import models


class Location(models.Model):
    """Location model."""

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField("Название", max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Площадка"
        verbose_name_plural = "Площадки"


class Event(models.Model):
    """Event model."""

    OPEN_STATUS = "open"
    CLOSED_STATUS = "closed"
    STATUS_TYPES = [(OPEN_STATUS, "Открыт"), (CLOSED_STATUS, "Закрыт")]

    id = models.UUIDField(primary_key=True, editable=False)
    name = models.CharField("Название", max_length=50, db_index=True)
    event_time = models.DateTimeField(
        "Дата и время проведения мероприятия", db_index=True
    )
    registration_deadline = models.DateTimeField(
        "Крайний срок регистрации", db_index=True
    )
    place = models.ForeignKey(
        "Location", blank=True, null=True, on_delete=models.SET_NULL
    )
    status = models.CharField("Текущий статус", choices=STATUS_TYPES, db_index=True)
    changed_at = models.DateTimeField("Дата и время изменения мероприятия")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"
