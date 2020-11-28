from django.utils import timezone
from rest_framework import mixins, generics, status, viewsets
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from lamusitheque.apiutils.permissions import IsUser
from export_ratings.api.serializers import ExportReadSerializer, ExportCreateSerializer
from export_ratings.models import ExportReport
from export_ratings.sc_scraper import ParseSCUser
from export_ratings.settings import get_min_export_timediff
from export_ratings.tasks import export_from_sc


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def parse_sc_user(request):
    username = request.GET.get("user")
    if username:
        parser = ParseSCUser(username)
        if parser.load():
            try:
                results = parser.get_user_data()
                return Response(results)
            except (TypeError, KeyError):
                raise NotFound
    raise NotFound


class ExportView(generics.ListCreateAPIView):
    """
    Creates or lists exports
    """

    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        return ExportReport.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ["GET"]:
            return ExportReadSerializer
        return ExportCreateSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user.username
        sc_user = serializer.validated_data["sc_url"].split("/")[-1]
        config = {el: True for el in serializer.validated_data["fields"]}
        erase = serializer.validated_data["erase"]

        user_exports = request.user.exports.order_by("-created_at")
        if user_exports.count() > 0:
            now = timezone.now()
            last_export = user_exports[0].created_at
            delta = now - last_export
            min_timediff = get_min_export_timediff()
            if delta.total_seconds() < min_timediff:
                return Response(
                    {"message": "An export has already been generated recently."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        # launch task
        export_from_sc.delay(
            username=user, sc_username=sc_user, config=config, erase_old=erase
        )

        return Response(
            {"message": "Export task has been launched"}, status.HTTP_202_ACCEPTED
        )


class ExportRetrieveViewset(viewsets.GenericViewSet, mixins.RetrieveModelMixin):

    permission_classes = (IsUser,)
    queryset = ExportReport.objects.all()
    serializer_class = ExportReadSerializer

    @action(detail=True, methods=["GET"])
    def new(self, request, pk):
        export = self.get_object()
        return Response({"new_ratings": export.new_ratings})

    @action(detail=True, methods=["GET"])
    def conflicts(self, request, pk):
        export = self.get_object()
        return Response({"conflicts": export.conflicts})

    @action(detail=True, methods=["GET"])
    def not_found(self, request, pk):
        export = self.get_object()
        return Response({"not_found": export.not_found})
