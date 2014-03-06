# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AMRSUser.role'
        db.add_column(u'amrs_user_validation_amrsuser', 'role',
                      self.gf('django.db.models.fields.CharField')(default='clinician', max_length=160),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AMRSUser.role'
        db.delete_column(u'amrs_user_validation_amrsuser', 'role')


    models = {
        u'amrs_user_validation.amrsuser': {
            'Meta': {'object_name': 'AMRSUser'},
            'cell_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_voided': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'requires_password_change': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'voided': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
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