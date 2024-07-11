from rest_framework import serializers

from app_category.models import Category



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'SortId',
            'CategoryId',
            'RefId',
            'Category',
            'SectionType',
            'CategoryType',
            'ActiveStatus'
        )