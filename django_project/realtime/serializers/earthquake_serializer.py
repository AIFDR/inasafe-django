# coding=utf-8
from builtins import object
import json

from django.core.urlresolvers import reverse
from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer)

from realtime.models.earthquake import Earthquake, EarthquakeReport, \
    EarthquakeMMIContour
from realtime.serializers.utilities import CustomSerializerMethodField

__author__ = 'Rizky Maulana Nugraha "lucernae" <lana.pcfre@gmail.com>'
__date__ = '19/06/15'


class EarthquakeReportSerializer(serializers.ModelSerializer):

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

    class Meta(object):
        model = EarthquakeReport
        fields = (
            'url',
            'shake_id',
            'source_type',
            'shake_url',
            'language',
            'report_pdf',
            'report_image',
            'report_thumbnail',
            'report_map_filename'
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
        :type obj: Earthquake
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

    def get_shake_grid(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: Earthquake
        :return:
        """
        if obj.shake_grid:
            return obj.shake_grid.url
        else:
            return obj.shake_grid_download_url

    shake_grid = CustomSerializerMethodField()

    class Meta(object):
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
            'source_type',
            'event_id_formatted',
            'shake_grid_download_url',
            'mmi_layer_download_url',
            'grid_xml_filename',
            'mmi_layer_filename',
            'mmi_layer_saved',
        )


class EarthquakeGeoJsonSerializer(GeoFeatureModelSerializer):

    def get_shake_grid(self, serializer_field, obj):
        """
        :param serializer_field:
        :type serializer_field: CustomSerializerMethodField
        :param obj:
        :type obj: Earthquake
        :return:
        """
        if obj.shake_grid:
            return obj.shake_grid.url
        else:
            return obj.shake_grid_download_url

    shake_grid = CustomSerializerMethodField()

    class Meta(object):
        model = Earthquake
        geo_field = "location"
        id = 'id'
        fields = (
            'shake_id',
            'shake_grid',
            # 'mmi_output',
            'magnitude',
            'time',
            'depth',
            'location',
            'location_description',
            'felt',
            'source_type',
            'event_id_formatted',
            'grid_xml_filename',
            'has_corrected',
            'mmi_layer_saved'
        )


class EarthquakeMMIContourGeoJSONSerializer(GeoFeatureModelSerializer):

    class Meta(object):
        model = EarthquakeMMIContour
        geo_field = 'geometry'
        id = 'id'

    def get_properties(self, instance, fields):
        return json.loads(instance.properties)
