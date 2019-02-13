from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.contrib.admin import SimpleListFilter
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _

from .constants import (MODERATION_READY_STATE,
                        MODERATION_DRAFT_STATE,
                        MODERATION_STATUS_REJECTED,
                        MODERATION_STATUS_APPROVED,
                        MODERATION_STATUS_PENDING)

from . import moderation


def _registered_content_types():
    "Return sorted content types for all registered models."
    content_types = []
    registered = list(moderation._registered_models.keys())
    registered.sort(key=lambda obj: obj.__name__)
    for model in registered:
        content_types.append(ContentType.objects.get_for_model(model))
    return content_types

class StatusFilter(SimpleListFilter):
    title = _('statut')

    parameter_name = 'statut'

    def lookups(self, request, model_admin):
        return (
            (None, _('En attente')),
            ('approved', _('Accepté')),
            ('rejected', _('Refusé')),
            ('all', _('Tout')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                    }, []),
                'display': title,
                }
    
    def queryset(self, request, queryset):
        if self.value() == 'approved':
            return queryset.filter(status=MODERATION_STATUS_APPROVED)
        elif self.value() == 'rejected':
            return queryset.filter(status=MODERATION_STATUS_REJECTED)
        elif self.value() == 'all':
            return queryset
        else:
            return queryset.filter(status=MODERATION_STATUS_PENDING)

try:
    from django.contrib.admin.filters import FieldListFilter
except ImportError:
    # Django < 1.4
    from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec

    class ContentTypeFilterSpec(RelatedFilterSpec):

        def __init__(self, *args, **kwargs):
            super(ContentTypeFilterSpec, self).__init__(*args, **kwargs)
            self.content_types = _registered_content_types()
            self.lookup_choices = [(ct.id, ct.name.capitalize()) for ct in
                                   self.content_types]

    def get_filter(f):
        return getattr(f, 'content_type_filter', False)
    FilterSpec.filter_specs.insert(0, (get_filter, ContentTypeFilterSpec))
else:
    # Django >= 1.4

    class RegisteredContentTypeListFilter(FieldListFilter):

        def __init__(self, field, request, params,
                     model, model_admin, field_path):
            self.lookup_kwarg = '%s' % field_path
            self.lookup_val = request.GET.get(self.lookup_kwarg)
            self.content_types = _registered_content_types()
            super(RegisteredContentTypeListFilter, self).__init__(
                field, request, params, model, model_admin, field_path)

        def expected_parameters(self):
            return [self.lookup_kwarg]

        def choices(self, cl):
            yield {
                'selected': self.lookup_val is None,
                'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
                'display': _('All')}
            for ct_type in self.content_types:
                yield {
                    'selected': smart_text(ct_type.id) == self.lookup_val,
                    'query_string': cl.get_query_string({
                        self.lookup_kwarg: ct_type.id}),
                    'display': str(ct_type),
                }
