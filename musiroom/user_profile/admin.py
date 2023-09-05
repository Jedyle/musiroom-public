from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profil"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "username",
        "email",
        "date_joined",
        "is_active",
        "is_staff",
        "first_name",
        "last_name",
        "get_birth",
        "get_sex",
        "get_description",
        "get_avatar",
    )

    def get_birth(self, instance):
        return instance.profile.birth

    get_birth.short_description = "Birth date"

    def get_sex(self, instance):
        return instance.profile.sex

    get_sex.short_description = "Gender"

    def get_description(self, instance):
        return instance.profile.description

    get_description.short_description = "Description"

    def get_avatar(self, instance):
        if instance.profile.avatar:
            return '<img src="{thumb}" />'.format(
                thumb=instance.profile.avatar.url,
            )
        else:
            return ""

    get_avatar.allow_tags = True
    get_avatar.short_description = "Avatar"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
