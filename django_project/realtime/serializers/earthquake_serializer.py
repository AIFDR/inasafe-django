# coding=utf-8
from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer
)

from realtime.models.earthquake import Earthquake, EarthquakeReport
from realtime.serializers.utilities import CustomSerializerMethodField

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


class EarthquakeReportSerializer(serializers.ModelSerializer):

    # def get_shake_id(self, serializer_field, obj):
    #     """
    #     :param serializer_field:
    #     :type serializer_field: CustomSerializerMethodField
    #     :param obj:
    #     :type obj: EarthquakeReport
    #     :return:
    #     """
    #     return obj.earthquake.shake_id
    #
    # def get_source_type(self, serializer_field, obj):
    #     """
    #     :param serializer_field:
    #     :type serializer_field: CustomSerializerMethodField
    #     :param obj:
    #     :type obj: EarthquakeReport
    #     :return:
    #     """
    #     return obj.earthquake.source_type

    def get_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: EarthquakeReport
        :return:
        """
        relative_uri = reverse(
            'realtime:earthquake_report_detail',
            kwargs={
                'shake_id': obj.earthquake.shake_id,
                'source_type': obj.earthquake.source_type,
                'language': obj.language})
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_url method
    url = CustomSerializerMethodField()

    def get_shake_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: EarthquakeReport
        :return:
        """
        relative_uri = reverse(
            'realtime:earthquake_detail',
            kwargs={
                'shake_id': obj.earthquake.shake_id,
                'source_type': obj.earthquake.source_type
            })
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_shake_url method
    shake_url = CustomSerializerMethodField()

    class Meta:
        model = EarthquakeReport
        fields = (
            'url',
            'shake_id',
            'source_type',
            'shake_url',
            'language',
            'report_pdf',
            'report_image',
            'report_thumbnail'
        )


class EarthquakeSerializer(serializers.ModelSerializer):
    reports = EarthquakeReportSerializer(
        many=True, required=False, write_only=False,
        read_only=True)

    def get_url(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: EarthquakeReport
        :return:
        """
        relative_uri = reverse(
            'realtime:earthquake_detail',
            kwargs={
                'shake_id': obj.shake_id,
                'source_type': obj.source_type})
        if self.context and 'request' in self.context:
            return self.context['request'].build_absolute_uri(relative_uri)
        else:
            return relative_uri

    # auto bind to get_url method
    url = CustomSerializerMethodField()

    class Meta:
        model = Earthquake
        fields = (
            'url',
            'shake_id',
            'shake_grid',
            'mmi_output',
            'magnitude',
            'time',
            'depth',
            'location',
            'location_description',
            'felt',
            'reports',
            'hazard_path',
            'source_type'
        )


class EarthquakeGeoJsonSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Earthquake
        geo_field = "location"
        id = 'id'
        fields = (
            'shake_id',
            'shake_grid',
            'shake_grid_download_url',
            'mmi_output',
            'analysis_zip_download_url',
            'magnitude',
            'time',
            'depth',
            'location',
            'location_description',
            'felt',
            'source_type')
