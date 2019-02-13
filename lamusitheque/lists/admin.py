from django.contrib import admin
from .models import ItemList, ListObject

# Register your models here.
admin.register(ItemList)

class ListObjectInline(admin.TabularInline):
    model = ItemList.albums.through
    verbose_name = 'Element'
    extra = 0

@admin.register(ItemList)
class ItemListAdmin(admin.ModelAdmin):
    inlines = []
    extra = 1
