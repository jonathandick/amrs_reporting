# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Report'
        db.create_table(u'report_report', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('template', self.gf('django.db.models.fields.CharField')(max_length=1000, null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('voided', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_voided', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'report', ['Report'])

        # Adding model 'ReportTable'
        db.create_table(u'report_reporttable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_table_sql', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'report', ['ReportTable'])

        # Adding model 'ReportMember'
        db.create_table(u'report_reportmember', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_id', self.gf('django.db.models.fields.IntegerField')()),
            ('report_table_id', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'report', ['ReportMember'])

        # Adding model 'ReportTableParameter'
        db.create_table(u'report_reporttableparameter', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('report_table_id', self.gf('django.db.models.fields.IntegerField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=160)),
            ('default_value', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('order_number', self.gf('django.db.models.fields.IntegerField')()),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'report', ['ReportTableParameter'])


    def backwards(self, orm):
        # Deleting model 'Report'
        db.delete_table(u'report_report')

        # Deleting model 'ReportTable'
        db.delete_table(u'report_reporttable')

        # Deleting model 'ReportMember'
        db.delete_table(u'report_reportmember')

        # Deleting model 'ReportTableParameter'
        db.delete_table(u'report_reporttableparameter')


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
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'order_number': ('django.db.models.fields.IntegerField', [], {}),
            'report_table_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['report']