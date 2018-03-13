# coding=utf-8
"""Model class for earthquake realtime."""
import json
import os

from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from realtime.app_settings import EARTHQUAKE_EVENT_REPORT_FORMAT
from realtime.utils import split_layer_ext


class Earthquake(models.Model):
    """Earthquake model."""
    class Meta:
        """Meta class."""
        app_label = 'realtime'
        unique_together = (('shake_id', 'source_type'), )

    shake_id = models.CharField(
        verbose_name=_('The Shake ID'),
        help_text=_('The Shake ID, which represents the time of the event.'),
        max_length='14',
        blank=False)
    shake_grid = models.FileField(
        verbose_name=_('Shake Grid XML File'),
        help_text=_('The Shake Grid to process'),
        upload_to='earthquake/grid',
        blank=True,
        null=True)
    shake_grid_xml = models.TextField(
        verbose_name=_('Shake Grid XML File Contents'),
        help_text=_('The content of shake grid file'),
        blank=True,
        null=True)
    mmi_output = models.FileField(
        verbose_name=_('MMI related file zipped'),
        help_text=_('MMI related file, layers, and data, zipped.'),
        upload_to='earthquake/mmi_output',
        blank=True,
        null=True)
    mmi_output_path = models.CharField(
        verbose_name=_('MMI related file path'),
        help_text=_('MMI related file path location'),
        max_length=255,
        blank=True,
        null=True,
        default=None)
    magnitude = models.FloatField(
        verbose_name=_('The magnitude'),
        help_text=_('The magnitude of the event.'))
    time = models.DateTimeField(
        verbose_name=_('Date and Time'),
        help_text=_('The time the shake happened.'),
        blank=False)
    generated_time = models.DateTimeField(
        verbose_name=_('Report Generated Date and Time'),
        help_text=_('The time the shake report generated.'),
        blank=True,
        null=True,
        default=None)
    depth = models.FloatField(
        verbose_name=_('The depth'),
        help_text=_('The depth of the event in km unit.'))
    location = models.PointField(
        verbose_name=_('Location'),
        help_text=_(
            'The location of the shake event in longitude and latitude.'),
        srid=4326,
        max_length=255,
        null=False,
        blank=False)
    location_description = models.CharField(
        verbose_name=_('Location Description'),
        help_text=_('The description of the location e.g "Bali".'),
        max_length=255)
    felt = models.BooleanField(
        verbose_name=_('Felt Earthquake'),
        help_text=_("Set to True if this particular event showed up as felt "
                    "Earthquake in BMKG's List"),
        default=False)
    source_type = models.CharField(
        verbose_name=_('Source Type'),
        help_text=_('Source type of shake grid'),
        max_length=30,
        default='initial')
    analysis_task_id = models.CharField(
        verbose_name=_('Analysis celery task id'),
        help_text=_('Task id for running analysis'),
        max_length=255,
        default='',
        blank=True)
    analysis_task_status = models.CharField(
        verbose_name=_('Analysis celery task status'),
        help_text=_('Task status for running analysis'),
        max_length=30,
        default='None',
        blank=True)
    analysis_task_result = models.TextField(
        verbose_name=_('Analysis celery task result'),
        help_text=_('Task result of analysis run'),
        default='',
        blank=True,
        null=True)
    report_task_id = models.CharField(
        verbose_name=_('Report celery task id'),
        help_text=_('Task id for creating analysis report.'),
        max_length=255,
        default='',
        blank=True)
    report_task_status = models.CharField(
        verbose_name=_('Report celery task status'),
        help_text=_('Task status for creating analysis report.'),
        max_length=30,
        default='None',
        blank=True)
    report_task_result = models.TextField(
        verbose_name=_('Report celery task result'),
        help_text=_('Task result of report generation'),
        default='',
        blank=True,
        null=True)
    hazard_path = models.CharField(
        verbose_name=_('Hazard Layer path'),
        help_text=_('Location of hazard layer'),
        max_length=255,
        default=None,
        null=True,
        blank=True)
    impact_file_path = models.CharField(
        verbose_name=_('Impact File path'),
        help_text=_('Location of impact file.'),
        max_length=255,
        default=None,
        blank=True,
        null=True)
    inasafe_version = models.CharField(
        verbose_name=_('InaSAFE version'),
        help_text=_('InaSAFE version being used'),
        max_length=10,
        default=None,
        null=True,
        blank=True)

    objects = models.GeoManager()

    def __unicode__(self):
        shake_string = u'Shake event [%s]' % self.shake_id
        if self.location_description.strip():
            shake_string += u' in %s' % self.location_description
        return shake_string

    def delete(self, using=None):
        # delete all report
        if self.shake_grid:
            self.shake_grid.delete()
        if self.mmi_output:
            self.mmi_output.delete()
        for report in self.reports.all():
            report.delete(using=using)
        super(Earthquake, self).delete(using=using)

    @property
    def hazard_layer_exists(self):
        """Return bool to indicate existences of hazard layer"""
        if self.hazard_path:
            return os.path.exists(self.hazard_path)
        return False

    @property
    def has_reports(self):
        """Check if event has report or not."""
        return self.reports.count()

    @property
    def impact_layer_exists(self):
        """Return bool to indicate existences of impact layers"""
        if self.impact_file_path:
            return os.path.exists(self.impact_file_path)
        return False

    @property
    def shake_grid_exists(self):
        return bool(self.shake_grid or self.shake_grid_xml)

    @property
    def mmi_layer_exists(self):
        """Return bool to indicate existences of impact layers"""
        if self.impact_file_path:
            return os.path.exists(self.mmi_output_path)
        return False

    @property
    def analysis_zip_path(self):
        """Return analysis zip path for download."""
        dirname = os.path.dirname(self.impact_file_path)
        basename = os.path.basename(self.impact_file_path)
        basename_without_ext = split_layer_ext(basename)[0]
        zip_path = os.path.join(dirname, basename_without_ext + '.zip')
        if os.path.exists(zip_path):
            return zip_path
        return None

    @property
    def shake_grid_download_url(self):
        if self.shake_grid_exists:
            return reverse('realtime:shake_grid', kwargs={
                'shake_id': self.shake_id,
                'source_type': self.source_type
            })
        return None

    @property
    def analysis_zip_download_url(self):
        if self.mmi_layer_exists:
            return reverse('realtime:analysis_zip', kwargs={
                'shake_id': self.shake_id,
                'source_type': self.source_type
            })
        return None

    @property
    def need_run_analysis(self):
        if (self.analysis_task_status and
                not self.analysis_task_status == 'None'):
            return False
        return True

    @property
    def need_generate_reports(self):
        if (self.report_task_status and
                not self.report_task_status == 'None'):
            return False
        return True

    @property
    def analysis_result(self):
        """Return dict of analysis result."""
        try:
            return json.loads(self.analysis_task_result)
        except (TypeError, ValueError):
            return {}

    @property
    def report_result(self):
        """Return dict of report result."""
        try:
            return json.loads(self.report_task_result)
        except (TypeError, ValueError):
            return {}

    def rerun_report_generation(self):
        """Rerun Report Generations"""

        # Delete existing reports
        reports = self.reports.all()

        for r in reports:
            r.delete()

        self.report_task_result = ''
        self.report_task_status = ''
        self.save()

    def rerun_analysis(self):
        """Rerurn Analysis"""

        # Delete existing reports
        reports = self.reports.all()

        for r in reports:
            r.delete()

        self.report_task_result = ''
        self.report_task_status = ''

        # Reset analysis state
        self.impact_file_path = ''
        self.analysis_task_result = ''
        self.analysis_task_status = ''
        self.save()


class EarthquakeReport(models.Model):
    """Earthquake Report Model."""

    class Meta:
        """Meta class."""
        app_label = 'realtime'
        unique_together = (('earthquake', 'language'),)

    earthquake = models.ForeignKey(
        Earthquake,
        related_name='reports')
    language = models.CharField(
        verbose_name=_('Language ID'),
        help_text=_('The language ID of the report'),
        max_length=4,
        default='id'
    )
    report_pdf = models.FileField(
        verbose_name=_('PDF Report'),
        help_text=_('The impact report stored as PDF'),
        upload_to='reports/earthquake/pdf',
        null=True)
    report_image = models.ImageField(
        verbose_name=_('Image Report'),
        help_text=_('The impact report stored as PNG File'),
        upload_to='reports/earthquake/png',
        null=True)
    report_thumbnail = models.ImageField(
        verbose_name=_('Image Report Thumbnail'),
        help_text=_('The thumbnail of the report stored as PNG File'),
        upload_to='reports/earthquake/thumbnail',
        null=True)

    def delete(self, using=None):
        # delete stored files
        self.report_pdf.delete()
        self.report_image.delete()
        self.report_thumbnail.delete()
        super(EarthquakeReport, self).delete(using=using)

    @property
    def shake_id(self):
        return self.earthquake.shake_id

    @property
    def source_type(self):
        return self.earthquake.source_type

    @property
    def report_map_filename(self):
        """Return standardized filename for report map."""
        return EARTHQUAKE_EVENT_REPORT_FORMAT.format(
            shake_id=self.earthquake.shake_id,
            source_type=self.earthquake.source_type,
            language=self.language,
            suffix='',
            extension='pdf')

    @property
    def report_image_filename(self):
        """Return standardized filename for report map."""
        return EARTHQUAKE_EVENT_REPORT_FORMAT.format(
            shake_id=self.earthquake.shake_id,
            source_type=self.earthquake.source_type,
            language=self.language,
            suffix='',
            extension='png')

    @property
    def report_thumbnail_filename(self):
        """Return standardized filename for report map."""
        return EARTHQUAKE_EVENT_REPORT_FORMAT.format(
            shake_id=self.earthquake.shake_id,
            source_type=self.earthquake.source_type,
            language=self.language,
            suffix='thumbnail',
            extension='png')
