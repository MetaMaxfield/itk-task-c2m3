from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView

from src.events.models import Event
from src.events.pagination import CustomCursorPagination
from src.events.serializers import EventListSerializer


class EventListView(ListAPIView):
    queryset = Event.objects.filter(status=Event.OPEN_STATUS).select_related("location")
    serializer_class = EventListSerializer
    pagination_class = CustomCursorPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "date",
    ]
    ordering_fields = [
        "date",
    ]
