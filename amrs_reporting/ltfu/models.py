from django.db import models
import MySQLdb as mdb
import amrs_settings
from amrs_interface.models import *

import requests
import json

class DefaulterCohort(models.Model):
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    cohort_uuid = models.CharField(max_length=500)
    location_id = models.IntegerField()
    location_uuid = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)

    def set_self(self,args):
        self.name = args['name']
        self.description = args['description']
        self.location_id = args['location_id']
        self.location_uuid = args['location_uuid']
        patient_uuids = args['patient_uuids']
        
        self.cohort_uuid = Cohort.create_cohort(args['name'],args['description'],patient_uuids)
        self.save()    

                
        
    def update_defaulter_cohort(self):
        headers = {'content-type': 'application/json'}
        url_cohort = amrs_settings.amrs_url + '/ws/rest/v1/cohort/' 
        patient_uuids = self.get_defaulter_uuids(self.location_id)

        if self.cohort_uuid is not None and self.cohort_uuid != '':

            url_cohort += self.cohort_uuid + '/member'
            req = requests.get(url_cohort + '?v=ref', auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
            vals = json.loads(req.text)

            # delete all members currently in cohort
            for member in vals['results']:
                
                split = member['links'][0]['uri'].split('/ws')
                url = amrs_settings.amrs_url + '/ws' + split[1]
                req = requests.delete(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
                try : 
                    vals = '' #json.loads(req.text)
                    if 'error' in vals:
                        print url
                        print 'error deleting member'
                except:
                    pass
            self.save() #update time_updated field
                    
            
        else :
            payload = {'name': self.name,
                       'description': self.description,
                       'memberIds':[],
                       }

            data = json.dumps(payload)
            req = requests.post(url_cohort, data, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
            vals = json.loads(req.text)
            if 'error' in vals:
                print 'error creating new cohort'
                return 'error'
            
            self.cohort_uuid = vals['uuid']
            self.save()


        # Rebuild cohort: add new members now qualifying. 
        # Remember this is a dynamic list and patients will qualify and disqualify on a daily basis
        for uuid in patient_uuids:
            payload = {'patient':uuid}
            data = json.dumps(payload)
            req = requests.post(url_cohort, data, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        
                


    def get_defaulter_list(self,uuids_in_use=[]):        
        location_ids = (self.location_id,)
        start_range_high_risk = 8
        start_range = 30
        end_range = 89
        limit = 100
        print 'uuids in use total: ' + str(len(uuids_in_use))
        uuids = OutreachFormSubmissionLog.objects.filter(date_submitted__gte=self.date_updated).values_list('patient_uuid',flat=True)
        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range_high_risk,start_range,end_range,location_ids,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit+len(uuids)+len(uuids_in_use))['rows']

        defaulters = []
        
        for row in table:
            if row['uuid'] not in uuids and row['uuid'] not in uuids_in_use and row['risk_category'] != 0:
                defaulters.append(row)
        
        return defaulters
        



    @staticmethod
    def get_defaulter_uuids(location_id):
        location_ids = (location_id,)
        start_range_high_risk = 8
        start_range = 30
        end_range = 89
        limit = 200

        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range_high_risk,start_range,end_range,location_ids,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit)['rows']
    
        patient_ids = []
        for row in table:
            patient_ids.append(str(row['uuid']))
        return patient_ids

    
    
    
    @staticmethod
    def delete_defaulter_cohort(cohort_uuid):
        url_cohort = amrs_settings.amrs_url + '/ws/rest/v1/cohort/' + cohort_uuid
        headers = {'content-type': 'application/json'}
        req = requests.delete(url_cohort, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)

        dc = DefaulterCohort.objects.get(cohort_uuid=cohort_uuid)
        dc.delete()
        
    

    
    @staticmethod
    def update_defaulter_cohorts():
        import time
        location_ids = [1,2,3,4,7,8,9,11,12,13,14,15,17,19,20,23,24,25,26,27,28,31,50,54,55,64,65,69,70,72,73,78,82,83,100,130,135]
        #location_ids = [1,2,3]
        cohorts = []
        for location_id in location_ids :
            location = Location.get_location(location_id)
            last_datetime = Encounter.get_last_date_created_db(location_id)
            '''
            if last_datetime :
                last_datetime = time.strptime(last_datetime,"%Y-%m-%d %H:%M:%S")
            '''
                

            dcs = DefaulterCohort.objects.filter(location_id=location_id)
            if dcs.count() > 0:
                dc = dcs[0]
                print 'dc not new'
            else :
                print 'creating new dc'
                name = location['name'] + ' Defaulter List'
                description = location['name'] + ' Defaulter List'
                dc = DefaulterCohort(name=name,description=description,location_id=location_id,location_uuid=location['uuid'])

            print str(location_id) + ' last encounter: ' + str(last_datetime)
            print 'dc last update: ' + str(dc.date_updated)

            import pytz
            import datetime
            utc=pytz.UTC

            if dc.date_updated is None or dc.date_updated <= utc.localize(last_datetime):
                dc.update_defaulter_cohort()
                cohorts.append(dc)

        return cohorts




class OutreachFormSubmissionLog(models.Model):
    patient_uuid = models.CharField(max_length=500)
    location_uuid = models.CharField(max_length=500)
    defaulter_cohort_uuid = models.CharField(max_length=500)
    date_submitted = models.DateTimeField(auto_now=True,db_index=True)
    creator = models.IntegerField(null=True)
    values = models.CharField(max_length=10000)
    enc_uuid = models.CharField(max_length=100,null=True,blank=True)
        
