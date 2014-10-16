from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
import amrs_settings
from amrs_interface.models import *
import requests
import json

class DefaulterCohortMember(models.Model):
    defaulter_cohort_id = models.IntegerField()
    patient_uuid = models.CharField(max_length=500)

    last_encounter_id = models.IntegerField()
    last_encounter_date = models.CharField(max_length=500)
    last_rtc_date = models.DateField(null=True)
    last_encounter_type = models.CharField(max_length=500)
    risk_category = models.IntegerField()    

    next_encounter_date = models.DateField(null=True)
    next_encounter_type = models.CharField(max_length=200,null=True)
    next_rtc_date = models.DateField(null=True)
    retired = models.BooleanField(default=False)
    date_retired = models.DateTimeField(null=True)

    def update_status(self,encounter=None):
        import datetime

        if encounter is None :
            encounter = RetentionDataset.get_encounter(self.last_encounter_id)
        self.next_encounter_date = encounter['next_appt_date']
        self.next_encounter_type = encounter['next_encounter_type']
        if self.next_encounter_date is not None:
            self.retired=True
            self.date_retired = datetime.datetime.today()            
        self.save()


    def get_patient_info(self):
        import datetime
        patient = Patient.get_patient_by_uuid(self.patient_uuid)
        patient['last_encounter_date'] = self.last_encounter_date
        patient['last_encounter_type'] = self.last_encounter_type
        patient['last_rtc_date'] = self.last_rtc_date
        patient['next_encounter_date'] = self.next_encounter_date
        patient['next_encounter_type'] = self.next_encounter_type
        patient['retired'] = self.retired
        patient['risk_category'] = self.risk_category
        patient['defaulter_cohort_member_id'] = self.id
        patient['uuid'] = self.patient_uuid

        if self.last_rtc_date and self.next_encounter_date is None :
            patient['days_since_rtc_date'] = (datetime.date.today() - self.last_rtc_date).days
        else : patient['days_since_rtc_date'] = None
        return patient


        

class DefaulterCohort(models.Model):
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=500)
    cohort_uuid = models.CharField(max_length=500,null=True)
    location_id = models.IntegerField()
    location_uuid = models.CharField(max_length=500)

    date_created = models.DateTimeField(auto_now_add=True)
    retired = models.BooleanField(default=False)
    date_retired = models.DateTimeField(null=True)

    
    @staticmethod
    def get_outreach_locations():
        location_ids = [1,2,3,4,7,8,9,11,12,13,14,15,17,19,20,23,24,25,26,27,28,31,50,54,55,64,65,69,70,72,73,78,82,83,100,130,135]
        return Location.get_locations(location_ids=location_ids)


    def set_self(self,args):
        self.name = args['name']
        self.description = args['description']
        self.location_id = args['location_id']
        self.location_uuid = args['location_uuid']
        self.save()
        self.set_members()


    # get first 100 patients currently meeting criteria as a defaulter
    def set_members(self,limit = 100):
        location_ids = (self.location_id,)
        start_range_high_risk = 14
        start_range = 30
        end_range = 89

        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range_high_risk,start_range,end_range,location_ids,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit)['rows']    
        for row in table:
            patient_uuid = str(row['uuid'])
            c = DefaulterCohortMember(defaulter_cohort_id = self.id,
                                      patient_uuid = patient_uuid,
                                      last_encounter_id = row['encounter_id'],
                                      last_encounter_date = row['encounter_datetime'],
                                      last_encounter_type = row['name'],
                                      last_rtc_date = row['rtc_date'],
                                      risk_category = row['risk_category']
                                      )
            c.save()
            
    @staticmethod
    def init():
        DefaulterCohort.objects.all().delete()
        DefaulterCohortMember.objects.all().delete()
        locations = DefaulterCohort.get_outreach_locations()
        for l in locations: 
            dc = DefaulterCohort(name=l['name'] + ' Defaulter Cohort',
                                 description = 'Defaulter list for ' + l['name'],
                                 location_id = l['location_id'],
                                 location_uuid = l['uuid'])
            dc.save()
            dc.set_members()

            


    @staticmethod
    def update_defaulter_cohorts():
        
        members = DefaulterCohortMember.objects.filter(retired=0)
        encounter_ids = members.values_list('last_encounter_id',flat=True)
        encounters = RetentionDataset.get_encounters(encounter_ids)
        d = {}
        for encounter in encounters:
            if encounter['next_appt_date'] is not None :
                d[encounter['encounter_id']] = encounter

        for member in members:
            if member.last_encounter_id in d:
                encounter = d[member.last_encounter_id]
                member.update_status(encounter)
            


    @staticmethod
    def create_defaulter_cohort(location_uuid=None,old_defaulter_cohort_id=None):
        if location_uuid:
            dcs = DefaulterCohort.objects.filter(location_uuid=location_uuid,retired=False)
        elif old_defaulter_cohort_id :
            dcs = DefaulterCohort.objects.filter(id=old_defaulter_cohort_id,retired=False)
        else : return None
        print dcs

        for dc in dcs :
            dc.retire()
        dc = dcs[0]

        new_dc = DefaulterCohort(name=dc.name,
                                 description = dc.description,
                                 location_id = dc.location_id,
                                 location_uuid = dc.location_uuid)
        new_dc.save()
        new_dc.set_members()
        return new_dc
        


    def delete_self(self):
        DefaulterCohortMember.objects.filter(defaulter_cohort_id=self.id).delete()
        self.delete()


    def retire(self):
        import datetime
        self.retired=1
        self.date_retired = datetime.datetime.today()
        self.save()


    def get_total_active(self):
        return DefaulterCohortMember.objects.filter(defaulter_cohort_id=self.id,retired=False).count()

    def get_total(self):
        return DefaulterCohortMember.objects.filter(defaulter_cohort_id=self.id).count()

    def get_members(self):
        return DefaulterCohortMember.objects.filter(defaulter_cohort_id=self.id)


    def get_active_members(self):
        return DefaulterCohortMember.objects.filter(defaulter_cohort_id=self.id,retired=False)



    def get_patients(self):
        members = DefaulterCohortMember.objects.filter(defaulter_cohort_id=self.id).order_by('retired')
        patients = []
        d = {}
        for member in members:
            p = member.get_patient_info()
            d[p['family_name']] = p

        for key in sorted(d.iterkeys()):
            patients.append(d[key])
                    
            
        return patients


    def get_json(self):
        patients = self.get_patients()
        d = {"name":self.name,"date_created":self.date_created,"patients":patients,"id":self.id,"location_uuid":self.location_uuid}
        d = json.dumps(d,cls=DjangoJSONEncoder)
        return d

                
    def get_cohort_stats(self):
        risk_categories = {0:'Being Traced',1:'high',2:'medium',3:'low',4:'LTFU',5:'no_rtc_date',6:'untraceable'}                
        parameter_values = (int(start_range_high_risk),int(start_range),int(end_range),location_ids,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit)['rows']
        
        counts = {'tracing':0,'high':0,'medium':0,'low':0,'LTFU':0,'total':0,'no_rtc_date':0,'untraceable':0,'on_list_two_weeks':0}
        total = 0
        per_day = {}
        for row in table:
            if row['risk_category'] >= 0 :
                
                if row['risk_category'] == 0 : counts['tracing'] += 1
                else : counts[risk_categories[row['risk_category']]] +=1            
                counts['total'] +=1

                if row['days_since_rtc'] : days_since_rtc = int(row['days_since_rtc'])
                else : days_since_rtc = (date.today() - row['encounter_datetime']).days

                if (row['risk_category'] == 1 and days_since_rtc >= 22) or days_since_rtc >=44 : counts['on_list_two_weeks'] += 1 

                if days_since_rtc < 30 : days_since_rtc -= 8
                else : days_since_rtc -= 30
                if days_since_rtc in per_day : per_day[days_since_rtc] += 1
                else : per_day[days_since_rtc] = 1

        
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
    def delete_defaulter_cohort(cohort_uuid):
        url_cohort = amrs_settings.amrs_url + '/ws/rest/v1/cohort/' + cohort_uuid
        headers = {'content-type': 'application/json'}
        req = requests.delete(url_cohort, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)

        dc = DefaulterCohort.objects.get(cohort_uuid=cohort_uuid)
        dc.delete()
        
    

    
    @staticmethod
    def update_defaulter_cohorts_2():
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
