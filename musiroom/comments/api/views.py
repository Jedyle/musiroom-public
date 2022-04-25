from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from comments.api.filters import CommentFilter
from comments.api.serializers import (
    ReadCommentSerializer,
    WriteCommentSerializer,
    UpdateCommentSerializer,
)
from comments.models import Comment
from musiroom.apiutils.mixins import VoteMixin
from musiroom.apiutils.permissions import IsUserOrReadOnly

MIN_TIME_BETWEEN_COMMENTS = 5  # in seconds


class CommentViewset(viewsets.ModelViewSet, VoteMixin):
    permission_classes = (IsUserOrReadOnly,)
    filter_class = CommentFilter

    def get_serializer_class(self):
        serializers = {
            "GET": ReadCommentSerializer,
            "PUT": UpdateCommentSerializer,
            "POST": WriteCommentSerializer,
        }
        return serializers.get(self.request.method, UpdateCommentSerializer)

    def get_queryset(self):
        return Comment.objects.filter(parent__isnull=True)

    def get_object(self):

        # overwrite this method because get_queryset only gets comments with no parent

        pk = self.kwargs["pk"]
        obj = get_object_or_404(Comment, id=pk)
        self.check_object_permissions(self.request, obj)
        return obj

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent = serializer.validated_data.get("parent")
        content_type = serializer.validated_data.get("content_type")
        object_pk = serializer.validated_data.get("object_pk")

        model_class = content_type.model_class()
        try:
            object = model_class.objects.get(id=object_pk)
        except:
            raise Http404

        if parent is not None and (
            parent.content_type != content_type or parent.object_pk != object_pk
        ):
            return Response(
                {
                    "message": "Parent and child comments must have the same target object."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        last_user_comment = (
            Comment.objects.filter(user=request.user).order_by("-submit_date").first()
        )
        if last_user_comment is not None:
            elapsed = timezone.now() - last_user_comment.submit_date
            if elapsed.total_seconds() <= MIN_TIME_BETWEEN_COMMENTS:
                return Response(
                    {"message": "Last comment is too recent"},
                    status=status.HTTP_403_FORBIDDEN,
                )

        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentChildrenViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ReadCommentSerializer
    filter_class = CommentFilter

    def get_queryset(self):
        comment_id = self.kwargs["comments_pk"]
        return get_object_or_404(Comment, id=comment_id).children
