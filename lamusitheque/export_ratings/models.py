from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
import json

# Create your models here.


def user_export_path(instance, filename):
    return 'reports/user_{}/{}.json'.format(instance.user.id, str(instance.created_at).replace(' ', '_').replace('.', '_'))

class ExportReport(models.Model):
    user = models.ForeignKey(User, related_name="exports",on_delete = models.CASCADE)
    created_at = models.DateTimeField('Date de création', auto_now_add=True)
    report = models.FileField("Rapport", null=True, blank=True, upload_to=user_export_path)

    def __str__(self):
        return "{}'s report on {}".format(self.user.username, self.created_at)

    def get_absolute_url(self):
        return reverse('export_ratings:get_export', args=[self.id])             

    def get_stats(self):
        self.report.open(mode = 'r')
        report_json = json.load(self.report)
        return {
            'id' : self.id,
            'site' : report_json['from'],
            'created_at': self.created_at,
            'erase_old' : report_json['erase_old'],
            'data_to_export' : report_json['what_to_export'],
            'new_ratings' : len(report_json['newly_created']),
            'conflicts' : len(report_json['conflicts']),
            'not_found' : len(report_json['not_found']),
            }

    def get_new_ratings(self):
        self.report.open(mode = 'r')
        report_json = json.load(self.report)
        return report_json['newly_created']

    def get_conflicts(self):
        self.report.open(mode = 'r')
        report_json = json.load(self.report)
        return report_json['conflicts']

    def get_not_found(self):
        self.report.open(mode = 'r')
        report_json = json.load(self.report)
        return report_json['not_found']

    class Meta:
        verbose_name="Export"
        verbose_name_plural="Exports"
