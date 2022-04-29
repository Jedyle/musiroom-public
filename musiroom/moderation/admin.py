from __future__ import unicode_literals

import django
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django import urls as urlresolvers
from django.forms.models import ModelForm
from django.utils.translation import gettext as _

from . import moderation
from .constants import (
    MODERATION_STATUS_REJECTED,
    MODERATION_STATUS_APPROVED,
    MODERATION_STATUS_PENDING,
)
from .diff import get_changes_between_models

try:
    from .filterspecs import RegisteredContentTypeListFilter, StatusFilter
except ImportError:
    # Django < 1.4
    available_filters = ("content_type", "status")
else:
    # Django >= 1.4
    available_filters = (
        ("content_type", RegisteredContentTypeListFilter),
        StatusFilter,
    )
from .forms import BaseModeratedObjectForm
from .helpers import automoderate
from .models import ModeratedObject
from .utils import django_17, django_110


def approve_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.approve(by=request.user)


approve_objects.short_description = _("Accepter les objets sélectionnés")


def reject_objects(modeladmin, request, queryset):
    for obj in queryset:
        obj.reject(by=request.user)


reject_objects.short_description = _("Rejeter les objets sélectionnés")


def set_objects_as_pending(modeladmin, request, queryset):
    queryset.update(status=MODERATION_STATUS_PENDING)


set_objects_as_pending.short_description = _(
    "Changer le statut des objets sélectionnés à 'en attente'"
)


class ModerationAdmin(admin.ModelAdmin):
    admin_integration_enabled = True

    def get_queryset(self, request):
        # Modified from django.contrib.admin.options.BaseModelAdmin
        qs = self.model._default_unmoderated_manager.get_queryset()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        if obj and self.admin_integration_enabled:
            self.form = self.get_moderated_object_form(obj.__class__)

        return super(ModerationAdmin, self).get_form(request, obj, **kwargs)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        if self.admin_integration_enabled:
            self.send_message(request, object_id)

        try:
            return super(ModerationAdmin, self).change_view(
                request, object_id, form_url=form_url, extra_context=extra_context
            )
        except TypeError:
            return super(ModerationAdmin, self).change_view(
                request, object_id, extra_context=extra_context
            )

    def send_message(self, request, object_id):
        try:
            obj = self.model.unmoderated_objects.get(pk=object_id)
            moderated_obj = ModeratedObject.objects.get_for_instance(obj)
            moderator = moderated_obj.moderator
            msg = self.get_moderation_message(
                moderated_obj.status,
                moderated_obj.reason,
                moderator.visible_until_rejected,
            )
        except ModeratedObject.DoesNotExist:
            msg = self.get_moderation_message()

        self.message_user(request, msg)

    def save_model(self, request, obj, form, change):
        obj.save()
        automoderate(obj, request.user)

    def get_moderation_message(
        self, status=None, reason=None, visible_until_rejected=False
    ):
        if status == MODERATION_STATUS_PENDING:
            if visible_until_rejected:
                return _(
                    "L'objet est visible sur le site, "
                    "il sera supprimé si un modérateur le rejette"
                )
            else:
                return _(
                    "L'objet n'est pas visible sur le site, "
                    "il sera visible si un modérateur l'accepte"
                )
        elif status == MODERATION_STATUS_REJECTED:
            return _("Objet rejeté par le modérateur, " "raison: %s" % reason)
        elif status == MODERATION_STATUS_APPROVED:
            return _("Objet accepté par le modérateur, " "et visible sur le site")
        elif status is None:
            return _("Cet objet n'est pas enregistré sur " "le système de modération.")

    def get_moderated_object_form(self, model_class):
        class ModeratedObjectForm(BaseModeratedObjectForm):
            class Meta:
                model = model_class
                if django_17():
                    fields = "__all__"

        return ModeratedObjectForm


class ModeratedObjectAdmin(admin.ModelAdmin):
    date_hierarchy = "created"
    list_display = ("content_object", "content_type", "created", "status", "by", "on")
    list_filter = available_filters
    change_form_template = "moderation/moderate_object.html"
    change_list_template = "moderation/moderated_objects_list.html"
    actions = [reject_objects, approve_objects, set_objects_as_pending]
    fieldsets = (("Object moderation", {"fields": ("reason",)}),)

    def get_actions(self, request):
        actions = super(ModeratedObjectAdmin, self).get_actions(request)
        # Remove the delete_selected action if it exists
        try:
            del actions["delete_selected"]
        except KeyError:
            pass
        return actions

    def content_object(self, obj):
        return str(obj.changed_object)

    def get_moderated_object_form(self, model_class):
        class ModeratedObjectForm(ModelForm):
            class Meta:
                model = model_class
                if django_17():
                    fields = "__all__"

        return ModeratedObjectForm

    def change_view(self, request, object_id, extra_context=None):
        moderated_object = ModeratedObject.objects.get(pk=object_id)

        changed_obj = moderated_object.changed_object

        moderator = moderation.get_moderator(changed_obj.__class__)

        if moderator.visible_until_rejected:
            old_object = changed_obj
            new_object = moderated_object.get_object_for_this_type()
        else:
            old_object = moderated_object.get_object_for_this_type()
            new_object = changed_obj

        changes = list(
            get_changes_between_models(
                old_object,
                new_object,
                moderator.fields_exclude,
                resolve_foreignkeys=moderator.resolve_foreignkeys,
            ).values()
        )

        if request.POST:
            admin_form = self.get_form(request, moderated_object)(request.POST)

            if admin_form.is_valid():
                reason = admin_form.cleaned_data["reason"]
                if "approve" in request.POST:
                    moderated_object.approve(request.user, reason)
                elif "reject" in request.POST:
                    moderated_object.reject(request.user, reason)

        content_type = ContentType.objects.get_for_model(changed_obj.__class__)
        try:
            object_admin_url = urlresolvers.reverse(
                "admin:%s_%s_change" % (content_type.app_label, content_type.model),
                args=(changed_obj.pk,),
            )
        except urlresolvers.NoReverseMatch:
            object_admin_url = None

        extra_context = {
            "changes": changes,
            "django_version": django.get_version()[:3],
            "object_admin_url": object_admin_url,
        }
        return super(ModeratedObjectAdmin, self).change_view(
            request, object_id, extra_context=extra_context
        )


admin.site.register(ModeratedObject, ModeratedObjectAdmin)
