from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, PageViewSet, CommentViewSet, MediaGalleryViewSet,
    check_slug, get_content_by_slug, get_all_slugs,
    pages_by_category, pages_by_category_slug
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'pages', PageViewSet, basename='page')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'media-gallery', MediaGalleryViewSet, basename='mediagallery')

urlpatterns = [
    path('slugs/check/', check_slug, name='check-slug'),
    path('slugs/getall/', get_all_slugs, name='get-all-slugs'),
    path('content/', get_content_by_slug, name='get-content-by-slug'),
    path('pages/by-category/<str:category_id>/', pages_by_category, name='pages-by-category'),
    path('pages/by-category-slug/<str:category_slug>/', pages_by_category_slug, name='pages-by-category-slug'),
    path('', include(router.urls)),
]
