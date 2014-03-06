# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Privilege'
        db.delete_table(u'amrs_user_validation_privilege')

        # Adding model 'Role'
        db.create_table(u'amrs_user_validation_role', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'amrs_user_validation', ['Role'])


    def backwards(self, orm):
        # Adding model 'Privilege'
        db.create_table(u'amrs_user_validation_privilege', (
            ('privilege', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'amrs_user_validation', ['Privilege'])

        # Deleting model 'Role'
        db.delete_table(u'amrs_user_validation_role')


    models = {
        u'amrs_user_validation.authorize': {
            'Meta': {'object_name': 'Authorize'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'amrs_user_validation.role': {
            'Meta': {'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['amrs_user_validation']