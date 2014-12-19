# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

from . import USER_ORM_LABEL
from . import USER_MODEL_LABEL
from . import User


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Drip'
        db.create_table('drip_drip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastchanged', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('enabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('subject_template', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('body_html_template', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('drip', ['Drip'])

        # Adding model 'SentDrip'
        db.create_table('drip_sentdrip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('drip', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_drips', to=orm['drip.Drip'])),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_drips', to=orm[USER_ORM_LABEL])),
            ('subject', self.gf('django.db.models.fields.TextField')()),
            ('body', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('drip', ['SentDrip'])

        # Adding model 'QuerySetRule'
        db.create_table('drip_querysetrule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('lastchanged', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('drip', self.gf('django.db.models.fields.related.ForeignKey')(related_name='queryset_rules', to=orm['drip.Drip'])),
            ('method_type', self.gf('django.db.models.fields.CharField')(default='filter', max_length=12)),
            ('field_name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('lookup_type', self.gf('django.db.models.fields.CharField')(default='exact', max_length=12)),
            ('field_value', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('drip', ['QuerySetRule'])


    def backwards(self, orm):
        # Deleting model 'Drip'
        db.delete_table('drip_drip')

        # Deleting model 'SentDrip'
        db.delete_table('drip_sentdrip')

        # Deleting model 'QuerySetRule'
        db.delete_table('drip_querysetrule')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        USER_MODEL_LABEL: {
            'Meta': {
                'object_name': User.__name__,
                'db_table': "'%s'" % User._meta.db_table
            },
            User._meta.pk.attname: (
                'django.db.models.fields.AutoField', [],
                {'primary_key': 'True',
                'db_column': "'%s'" % User._meta.pk.column}
            ),
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'drip.drip': {
            'Meta': {'object_name': 'Drip'},
            'body_html_template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'enabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastchanged': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'subject_template': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'drip.querysetrule': {
            'Meta': {'object_name': 'QuerySetRule'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'drip': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'queryset_rules'", 'to': "orm['drip.Drip']"}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'field_value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastchanged': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'lookup_type': ('django.db.models.fields.CharField', [], {'default': "'exact'", 'max_length': '12'}),
            'method_type': ('django.db.models.fields.CharField', [], {'default': "'filter'", 'max_length': '12'})
        },
        'drip.sentdrip': {
            'Meta': {'object_name': 'SentDrip'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'drip': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_drips'", 'to': "orm['drip.Drip']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subject': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_drips'", 'to': "orm['{0}']".format(USER_ORM_LABEL)})
        }
    }

    complete_apps = ['drip']
