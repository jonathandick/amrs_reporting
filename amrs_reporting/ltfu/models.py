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


    @staticmethod
    def get_defaulter_patient_ids(location_id):
        location_ids = (location_id,)
        start_range_high_risk = 8
        start_range = 30
        end_range = 89
        
        limit = 200
        risk_categories = {0:'Being Traced',1:'high',2:'medium',3:'low',4:'LTFU',5:'no_rtc_date',6:'untraceable'}    

        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range_high_risk,start_range,end_range,location_id,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit)['rows']
    
        patient_ids = []
        for row in table:
            patient_ids.append(row.person_id)        
        return patient_ids


    def update_cohort(self):
        url_cohort = 'https://testserver1.ampath.or.ke:8443/amrs/ws/rest/v1/cohort/' + self.cohort_uuid        
        headers = {'content-type': 'application/json'}
        req = requests.get(url_cohort, auth=(amrs_settings.username,amrs_settings.password),headers=headers)                        
        vals = json.loads(req.text)
        if 'error' in vals:
            print 'there was an error'
            return 'error'                
        
        patient_ids = self.get_defaulter_patient_ids

        payload = {'name': self.name,
                   'description': self.description,
                   'memberIds':patient_ids,
                   }
        data = json.dumps(payload)
        req = requests.post(url_cohort, data, auth=(amrs_settings.username,amrs_settings.password),headers=headers)
        vals = json.loads(req.text)
        if 'error' in vals:
            print 'error creating new cohort'
            return 'error'
        
        self.uuid = vals['uuid']
        self.save()
    
    
    
    @staticmethod
    def create_defaulter_lists(self):
        locations_ids = [1,13,14,15]
        for id in location_ids :
            location = Location.get_location(id)
            
            name = location.name + ' Defaulter List'
            description = location.name + ' Defaulter List'
            patient_ids = DefaulterCohort.get_defaulter_patient_ids(id)

            url_cohort = 'https://testserver1.ampath.or.ke:8443/amrs/ws/rest/v1/cohort'  
            headers = {'content-type': 'application/json'}
            payload = {'name': name,
                       'description': description,
                       'memberIds':patient_ids,
                       }
            data = json.dumps(payload)
            req = requests.post(url_cohort, data, auth=(amrs_settings.username,amrs_settings.password),headers=headers)
            
            vals = json.loads(req.text)
            if 'error' in vals:
                print 'error creating new cohort'
                return 'error'
            
            dc = DefaulterCohort()        
            dc.name = name
            dc.description = description
            dc.uuid = vals['uuid']
            dc.save()
            
            
            
