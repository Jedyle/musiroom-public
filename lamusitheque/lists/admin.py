from django.contrib import admin

from .models import ListObj

# Register your models here.
admin.register(ListObj)


class ListObjectInline(admin.TabularInline):
    model = ListObj.albums.through
    verbose_name = 'Element'
    extra = 0


@admin.register(ListObj)
class ListObjAdmin(admin.ModelAdmin):
    inlines = []
    extra = 1
