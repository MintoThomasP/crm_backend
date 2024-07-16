from rest_framework import serializers

from app_category.models import Category, Report



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




class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = (
            'SortId',
            'ReportId',
            'ReportType',
            'Month',
            'Year',
            'ClientId',
            'CategoryId',
            'Amount',
            'Comment',
            'OrderNo',
            'Level'
        )