from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from .models import Category, Page, Comment, MediaGallery, GlobalSlug
from .serializers import (
    CategorySerializer, PageSerializer,
    CommentSerializer, MediaGallerySerializer
)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage hierarchical category models.
    Supports self-referencing hierarchy listings and recursive child nodes.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        """
        Optional query parameter support:
        `?top_level=true` filters the category list to top-level records only.
        This provides a clean entry point for UI select trees.
        """
        queryset = super().get_queryset()
        top_level = self.request.query_params.get('top_level', None)
        if top_level is not None and top_level.lower() == 'true':
            return queryset.filter(parent__isnull=True)
        return queryset


class PageViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage built CMS pages.
    Integrates writable nested transactional SEO metadata configurations.
    """
    queryset = Page.objects.all()
    serializer_class = PageSerializer

    @action(detail=True, methods=['post'], url_path='increment-view')
    def increment_view(self, request, pk=None):
        """
        Safely increments the page's visitor view analytics count.
        Leverages Django F expressions to perform atomic increments inside MySQL
        to eliminate database concurrency write race conditions.
        """
        page = self.get_object()

        # Atomically increment in DB without load-save race hazards
        page.user_view_count = F('user_view_count') + 1
        page.save(update_fields=['user_view_count'])

        # Refresh from database memory layer to fetch updated count for serialization response
        page.refresh_from_db()

        return Response({
            'status': 'Page visitor view counter incremented successfully.',
            'id': page.id,
            'title': page.title,
            'slug': page.slug,
            'user_view_count': page.user_view_count
        }, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage reader feedback comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    filterset_fields = ['page']  # Filter comment list logs by page ID

    def get_queryset(self):
        queryset = super().get_queryset()
        page_id = self.request.query_params.get('page', None)
        if page_id is not None:
            return queryset.filter(page_id=page_id)
        return queryset


class MediaGalleryViewSet(viewsets.ModelViewSet):
    """
    ViewSet to manage centralized media assets and gallery queries.
    """
    queryset = MediaGallery.objects.all()
    serializer_class = MediaGallerySerializer


@api_view(['GET'])
def check_slug(request):
    """
    Check if a slug is globally available across all entities.
    Query params:
        slug (str): The slug to check
    Returns:
        {"available": bool, "entity_type": str|null}
    """
    slug = request.query_params.get('slug')
    if not slug:
        return Response({'error': 'slug query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    qs = GlobalSlug.objects.filter(slug=slug)
    if qs.exists():
        global_slug = qs.first()
        entity_type = "page" if global_slug.page else "category" if global_slug.category else "unknown"
        return Response({
            'available': False,
            'entity_type': entity_type
        }, status=status.HTTP_200_OK)

    return Response({'available': True, 'entity_type': None}, status=status.HTTP_200_OK)


@api_view(['POST'])
def get_content_by_slug(request):
    """
    Retrieve content dynamically based on a global slug.
    If it's a category, returns category data + associated pages.
    If it's a page, returns page data.
    Expects JSON body: {"slug": "..."}
    """
    slug = request.data.get('slug')
    if not slug:
        return Response({'error': 'Slug is required in the request body.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        global_slug = GlobalSlug.objects.get(slug=slug)
    except GlobalSlug.DoesNotExist:
        return Response({'error': 'Slug not found'}, status=status.HTTP_404_NOT_FOUND)

    if global_slug.category:
        category_data = CategorySerializer(
            global_slug.category, context={'request': request}).data
        pages = Page.objects.filter(category=global_slug.category)
        pages_data = PageSerializer(pages, many=True, context={
                                    'request': request}).data
        return Response({
            'type': 'category',
            'data': category_data,
            'pages': pages_data
        }, status=status.HTTP_200_OK)

    elif global_slug.page:
        page_data = PageSerializer(global_slug.page, context={
                                   'request': request}).data
        return Response({
            'type': 'page',
            'data': page_data
        }, status=status.HTTP_200_OK)

    return Response({'error': 'Slug has no associated content'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_all_slugs(request):
    """
    Retrieve all global slug data records.
    """
    slugs = GlobalSlug.objects.all().order_by('slug')
    data = []
    for s in slugs:
        entity_type = "page" if s.page else "category" if s.category else "unknown"
        entity_id = s.page.id if s.page else s.category.id if s.category else None
        entity_title = s.page.title if s.page else s.category.name if s.category else ""
        data.append({
            'slug': s.slug,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'entity_title': entity_title,
            'created_at': s.created_at
        })
    return Response(data, status=status.HTTP_200_OK)
