from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from comments.api.filters import CommentFilter
from comments.api.permissions import IsCommentOwnerOrReadOnly
from comments.api.serializers import ReadCommentSerializer, WriteCommentSerializer, UpdateCommentSerializer
from comments.models import Comment
from lamusitheque.apiutils.serializers import VoteSerializer

MIN_TIME_BETWEEN_COMMENTS = 5  # in seconds


class CommentViewset(viewsets.ModelViewSet):
    permission_classes = (IsCommentOwnerOrReadOnly,)
    filter_class = CommentFilter

    def get_serializer_class(self):
        serializers = {
            "GET": ReadCommentSerializer,
            "PUT": UpdateCommentSerializer,
            "POST": WriteCommentSerializer
        }
        return serializers.get(self.request.method, UpdateCommentSerializer)

    def get_queryset(self):
        return Comment.objects.filter(parent__isnull=True)

    def get_object(self):

        # overwrite this method because get_queryset only gets comments with no parent

        pk = self.kwargs["pk"]
        return get_object_or_404(Comment, id=pk)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        parent = serializer.validated_data.get('parent')
        content_type = serializer.validated_data.get('content_type')
        object_pk = serializer.validated_data.get('object_pk')

        model_class = content_type.model_class()
        try:
            object = model_class.objects.get(id=object_pk)
        except:
            raise Http404

        if parent is not None and (parent.content_type != content_type or parent.object_pk != object_pk):
            return Response({
                "message": "Parent and child comments must have the same target object."
            }, status=status.HTTP_400_BAD_REQUEST)

        last_user_comment = Comment.objects.filter(user=request.user).order_by('-submit_date').first()
        if last_user_comment is not None:
            elapsed = timezone.now() - last_user_comment.submit_date
            if elapsed.total_seconds() <= MIN_TIME_BETWEEN_COMMENTS:
                return Response({
                    "message": "Last comment is too recent"
                }, status=status.HTTP_403_FORBIDDEN)

        serializer.save(user=request.user)
        return Response(serializer.data)

    @action(detail=True, methods=["PUT"])
    def vote(self, request, pk=None):
        # votes
        # TODO : change default form in browsable API
        serializer = VoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vote = serializer.validated_data.get('vote')
        comment = self.get_object()
        if vote == "up":
            comment.votes.up(request.user.pk)
        elif vote == "down":
            comment.votes.down(request.user.pk)
        else:
            comment.votes.delete(request.user.pk)
        # re-call get object to have the updated instance
        # (doesn't update by itself, don't know why)
        comment = self.get_object()
        serializer = self.get_serializer(comment)
        return Response(serializer.data)



class CommentChildrenViewset(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = ReadCommentSerializer
    filter_class = CommentFilter

    def get_queryset(self):
        print(self.kwargs)
        comment_id = self.kwargs['comments_pk']
        return get_object_or_404(Comment, id=comment_id).children
