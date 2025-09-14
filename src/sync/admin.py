# Register your models here.
from django.contrib import admin

from src.sync.models import SyncResult

admin.site.register(SyncResult)
