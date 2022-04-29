from django.urls import re_path

from . import views  # import views so we can use them in urls.

app_name = "export_ratings"

urlpatterns = [
    re_path(r"^creer/$", views.create_export, name="create_export"),
    re_path(r"^senscritique/donnees/$", views.parse_sc_user, name="parse_sc_user"),
    re_path(r"^(?P<export_id>[0-9]+)/$", views.get_export, name="get_export"),
    re_path(
        r"^(?P<export_id>[0-9]+)/nouveaux/$",
        views.get_new_ratings,
        name="get_new_ratings",
    ),
    re_path(
        r"^(?P<export_id>[0-9]+)/conflits/$", views.get_conflicts, name="get_conflicts"
    ),
    re_path(
        r"^(?P<export_id>[0-9]+)/echecs/$", views.get_not_found, name="get_not_found"
    ),
]
