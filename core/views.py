from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response

from .serializers import PostSerializer, ContactSerializer
from .models import Post
from rest_framework import permissions
from rest_framework import pagination
from rest_framework import generics
from taggit.models import Tag
from .serializers import TagSerializer
from rest_framework.views import APIView
from django.core.mail import send_mail


class PageNumberSetPagination(pagination.PageNumberPagination):
    page_size = 6
    page_size_query_param = 'page_size'
    ordering = 'created_at'


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]
    pagination_class = PageNumberSetPagination


class TagDetailView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = PageNumberSetPagination
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        tag_slug = self.kwargs['tag_slug'].lower()
        tag = Tag.objects.get(slug=tag_slug)
        return Post.objects.filter(tags=tag)


class TagView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class AsideView(generics.ListAPIView):
    queryset = Post.objects.all().order_by('-id')[:5]
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]


class FeedBackView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ContactSerializer

    def post(self, request, *args, **kwargs):
        serializer_class = ContactSerializer(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            name = data.get('name')
            from_email = data.get('email')
            subject = data.get('subject')
            message = data.get('message')
            send_mail(subject=f'От {name}({from_email}) | {subject}',
                      message=message,
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[settings.EMAIL_HOST_USER])
            return Response({"success": "Sent"})
