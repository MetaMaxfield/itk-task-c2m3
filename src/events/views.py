from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from src.events.models import Event
from src.events.pagination import CustomCursorPagination
from src.events.serializers import EventListSerializer


class EventListView(ListAPIView):
    authentication_classes = [
        JWTAuthentication,
    ]
    permission_classes = [
        IsAuthenticated,
    ]
    queryset = Event.objects.filter(status=Event.OPEN_STATUS).select_related("place")
    serializer_class = EventListSerializer
    pagination_class = CustomCursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "event_time",
        "registration_deadline",
        "status",
        "name",  # временное решение поиска "name" (ищем exact с помощью django-filter)
    ]
    ordering_fields = [
        "event_time",
    ]
