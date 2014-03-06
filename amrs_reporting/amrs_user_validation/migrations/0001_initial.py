# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Authorize'
        db.create_table(u'amrs_user_validation_authorize', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'amrs_user_validation', ['Authorize'])

        # Adding model 'Privilege'
        db.create_table(u'amrs_user_validation_privilege', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user_id', self.gf('django.db.models.fields.IntegerField')()),
            ('privilege', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'amrs_user_validation', ['Privilege'])


    def backwards(self, orm):
        # Deleting model 'Authorize'
        db.delete_table(u'amrs_user_validation_authorize')

        # Deleting model 'Privilege'
        db.delete_table(u'amrs_user_validation_privilege')


    models = {
        u'amrs_user_validation.authorize': {
            'Meta': {'object_name': 'Authorize'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'amrs_user_validation.privilege': {
            'Meta': {'object_name': 'Privilege'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privilege': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['amrs_user_validation']