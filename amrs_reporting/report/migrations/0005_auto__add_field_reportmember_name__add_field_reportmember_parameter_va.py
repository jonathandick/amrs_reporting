# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ReportMember.name'
        db.add_column(u'report_reportmember', 'name',
                      self.gf('django.db.models.fields.CharField')(max_length='300', null=True, blank=True),
                      keep_default=False)

        # Adding field 'ReportMember.parameter_values'
        db.add_column(u'report_reportmember', 'parameter_values',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'ReportMember.index'
        db.add_column(u'report_reportmember', 'index',
                      self.gf('django.db.models.fields.IntegerField')(default=-1),
                      keep_default=False)

        # Adding field 'ReportMember.title'
        db.add_column(u'report_reportmember', 'title',
                      self.gf('django.db.models.fields.TextField')(null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ReportMember.name'
        db.delete_column(u'report_reportmember', 'name')

        # Deleting field 'ReportMember.parameter_values'
        db.delete_column(u'report_reportmember', 'parameter_values')

        # Deleting field 'ReportMember.index'
        db.delete_column(u'report_reportmember', 'index')

        # Deleting field 'ReportMember.title'
        db.delete_column(u'report_reportmember', 'title')


    models = {
        u'report.report': {
            'Meta': {'object_name': 'Report'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_voided': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'voided': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'report.reportmember': {
            'Meta': {'object_name': 'ReportMember'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': "'300'", 'null': 'True', 'blank': 'True'}),
            'parameter_values': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'report_id': ('django.db.models.fields.IntegerField', [], {}),
            'report_table_id': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        u'report.reporttable': {
            'Meta': {'object_name': 'ReportTable'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'report_table_sql': ('django.db.models.fields.TextField', [], {})
        },
        u'report.reporttableparameter': {
            'Meta': {'object_name': 'ReportTableParameter'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'index': ('django.db.models.fields.IntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'report_table_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['report']