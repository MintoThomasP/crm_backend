from rest_framework import serializers

from app_category.models import Category, Report, ReportRefFile



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
            'ActiveStatus',
            'CompanyId'
        )




class ReportSaveSerializer(serializers.ModelSerializer):
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
            'Level',
            'Status'
        )
        
class ReportRefFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportRefFile
        fields = '__all__'

class ReportSerializer(serializers.ModelSerializer):
    RefFiles = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = Report
        fields = '__all__'

    def create(self, validated_data):
        files_data = validated_data.pop('RefFiles', None)
        report = Report.objects.create(**validated_data)
        if files_data:
            for file_data in files_data:
                ReportRefFile.objects.create(ReportId=report, ReportRefFile=file_data)
        return report
    def update(self, instance, validated_data):
        ref_files_data = validated_data.pop('RefFiles', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ref_files_data is not None:
            for file_data in ref_files_data:
                ReportRefFile.objects.create(ReportId=instance, ReportRefFile=file_data)
        
        return instance
    
# class BulkReportSerializer(serializers.Serializer):
#     reports = serializers.ListField(
#         child=ReportSerializer()
#     )

class SaveReportRefFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportRefFile
        fields = (
            'SortId',
            'ReportRefFileId',
            'ReportRefFile',
            'OrderNo'
        )
