# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'ReportTableParameter.order_number'
        db.delete_column(u'report_reporttableparameter', 'order_number')

        # Adding field 'ReportTableParameter.index'
        db.add_column(u'report_reporttableparameter', 'index',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'ReportTableParameter.order_number'
        db.add_column(u'report_reporttableparameter', 'order_number',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'ReportTableParameter.index'
        db.delete_column(u'report_reporttableparameter', 'index')


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
            'report_id': ('django.db.models.fields.IntegerField', [], {}),
            'report_table_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'report.reporttable': {
            'Meta': {'object_name': 'ReportTable'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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