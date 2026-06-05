import re
from django.db import transaction
from rest_framework import serializers
from .models import Category, Page, PageSEOMeta, Comment, MediaGallery, GlobalSlug

class GlobalSlugValidator:
    requires_context = True

    def __call__(self, value, serializer_field):
        instance = getattr(serializer_field.parent, 'instance', None)
        qs = GlobalSlug.objects.filter(slug=value)
        if qs.exists():
            global_slug = qs.first()
            if instance and hasattr(instance, 'global_slug') and getattr(instance.global_slug, 'slug', None) == value:
                return  # It's an update on the same entity keeping its slug
            entity_name = "Page" if global_slug.page else "Category" if global_slug.category else "another entity"
            raise serializers.ValidationError(f"This slug is already in use by {entity_name}.")

# Custom slug formatting check for DRF serializer validation
def validate_slug_format(value):
    slug_pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    if not re.match(slug_pattern, value):
        raise serializers.ValidationError(
            "Format error: The slug must contain only lowercase alphanumeric characters and hyphens, and cannot start or end with a hyphen."
        )
    return value


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        max_length=255,
        validators=[validate_slug_format, GlobalSlugValidator()],
        source='global_slug.slug'
    )
    # Self-referencing recursive nested structures serializer
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'parent', 'name', 'slug', 'short_description', 
            'description', 'image', 'icon', 'subcategories'
        ]

    @transaction.atomic
    def create(self, validated_data):
        global_slug_data = validated_data.pop('global_slug', None)
        category = super().create(validated_data)
        if global_slug_data and 'slug' in global_slug_data:
            GlobalSlug.objects.create(slug=global_slug_data['slug'], category=category)
        return category

    @transaction.atomic
    def update(self, instance, validated_data):
        global_slug_data = validated_data.pop('global_slug', None)
        category = super().update(instance, validated_data)
        if global_slug_data and 'slug' in global_slug_data:
            new_slug = global_slug_data['slug']
            if not hasattr(category, 'global_slug') or not category.global_slug or category.global_slug.slug != new_slug:
                if hasattr(category, 'global_slug') and category.global_slug:
                    category.global_slug.delete()
                GlobalSlug.objects.create(slug=new_slug, category=category)
        return category

    def get_subcategories(self, obj):
        # Recursively serialize child categories in nested list format
        children = obj.subcategories.all()
        if children.exists():
            return CategorySerializer(children, many=True, context=self.context).data
        return []


class PageSEOMetaSerializer(serializers.ModelSerializer):
    # Optional nested JSON field validator for json-ld format checks
    schema_json = serializers.JSONField(required=False)

    class Meta:
        model = PageSEOMeta
        exclude = ['page']  # Exclude page since it is set on save by the parent PageSerializer


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class MediaGallerySerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)
    file_name = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = MediaGallery
        fields = ['id', 'image', 'file_name', 'uploaded_at']

    def create(self, validated_data):
        image_file = validated_data.get('image')
        if image_file and not validated_data.get('file_name'):
            validated_data['file_name'] = image_file.name
        return super().create(validated_data)


class PageSerializer(serializers.ModelSerializer):
    slug = serializers.CharField(
        max_length=255,
        validators=[validate_slug_format, GlobalSlugValidator()],
        source='global_slug.slug'
    )
    # Nested OneToOne PageSEOMeta field mapping
    seo_meta = PageSEOMetaSerializer(required=False)
    
    # Read-only attributes
    user_view_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Page
        fields = [
            'id', 'category', 'title', 'slug', 'json_data', 
            'compiled_html', 'user_view_count', 'seo_meta', 
            'created_at', 'updated_at'
        ]

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new Page and its associated PageSEOMeta records atomically.
        """
        seo_meta_data = validated_data.pop('seo_meta', None)
        global_slug_data = validated_data.pop('global_slug', None)
        
        # Create page instance
        page = Page.objects.create(**validated_data)
        
        if global_slug_data and 'slug' in global_slug_data:
            GlobalSlug.objects.create(slug=global_slug_data['slug'], page=page)
        
        # Initialize default or provided SEO settings record
        if seo_meta_data is not None:
            PageSEOMeta.objects.create(page=page, **seo_meta_data)
        else:
            # Pre-seed a default fallback SEO meta record based on page title
            slug_val = global_slug_data['slug'] if global_slug_data else f"page-{page.id}"
            PageSEOMeta.objects.create(
                page=page,
                meta_title=page.title,
                meta_description=f"Auto-generated search engine description meta tags details for page {page.title}.",
                canonical_url=f"https://mysite.com/{slug_val}",
                robots_meta="index, follow"
            )
            
        return page

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Atomically update the Page instance and its nested PageSEOMeta relations.
        """
        seo_meta_data = validated_data.pop('seo_meta', None)
        global_slug_data = validated_data.pop('global_slug', None)

        # Standard Page fields update
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if global_slug_data and 'slug' in global_slug_data:
            new_slug = global_slug_data['slug']
            if not hasattr(instance, 'global_slug') or not instance.global_slug or instance.global_slug.slug != new_slug:
                if hasattr(instance, 'global_slug') and instance.global_slug:
                    instance.global_slug.delete()
                GlobalSlug.objects.create(slug=new_slug, page=instance)

        # Update or create the child SEO settings
        if seo_meta_data is not None:
            seo_meta, created = PageSEOMeta.objects.get_or_create(page=instance)
            for attr, value in seo_meta_data.items():
                setattr(seo_meta, attr, value)
            seo_meta.save()

        return instance
