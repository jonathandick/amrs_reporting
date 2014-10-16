from django.db import models
from amrs_interface.models import *
# Create your models here.


class EncounterForm():

    @staticmethod
    def get_obs(args):
        obs = []
        for key,value in args.iteritems():
            if key.startswith('obs__') and value.strip() != '':
                question_uuid = key[5:]
                l = args.getlist(key)
                for val in l:
                    obs.append({'concept':question_uuid,'value':val})
        return obs
    

    @staticmethod
    def get_person_attributes(args):
        attrs = []
        for key,value in args.iteritems():
            if key.startswith('attr__') and value.strip() != '':
                attr_type_uuid = key[6:]
                attrs.append({'person_attribute_type_uuid':attr_type_uuid,'value':value})
        return attrs


    @staticmethod
    def set_person_attributes(args):
        patient_uuid = args.get('patient_uuid',None)        
        attrs = []
        for key,value in args.iteritems():
            if key.startswith('attr__') and value.strip() != '':
                attr_type_uuid = key[6:]
                PersonAttribute.create_person_attribute_rest(patient_uuid,attr_type_uuid,value)
                



    @staticmethod
    def set_dead(form_args):
        patient_uuid = form_args.get('patient_uuid',None)
        death_date = form_args.get('obs__a89df3d6-1350-11df-a1f1-0026b9348838',None)
        cause_of_death = form_args.get('obs__a89df750-1350-11df-a1f1-0026b9348838',None)
        result = Person.set_dead(patient_uuid,death_date,cause_of_death)        
        return result


    @staticmethod
    def is_equal(enc1, enc2):
        try :
            obs1 = {}
            obs = enc1.pop('obs')

            for o in obs:
                enc1[o['concept']] = o['value']
        
            obs = enc2.pop('obs')
            for o in obs:
                enc2[o['concept']] = o['value']
        
            shared = set(enc1.items()) & set(enc2.items())
            return ((len(enc1) - len(shared)) == 0) and ((len(enc2) - len(shared)) == 0)
        except Exception, e:
            print e
        return False
    
    
    '''
    Check for equivalence of encounters. It seems that some of time, encounters are being submitted more than once
    '''
    @staticmethod
    def is_duplicate(patient_uuid,encounter_datetime,location_uuid,encounter_type_uuid,provider_uuid,obs):
        enc1 = {'patient':patient_uuid,
                'encounterDatetime':encounter_datetime,
                'location':location_uuid,
                'encounterType':encounter_type_uuid,
                'provider':provider_uuid,
                'obs': obs
                }
 
        logs = EncounterLog.objects.filter(patient_uuid=patient_uuid,encounter_datetime=encounter_datetime)
        for l in logs:
            rest_log = RESTLog.objects.get(id=l.rest_log_id)
            enc2 = json.loads(rest_log.payload)
            if EncounterForm.is_equal(enc1,enc2):
                return True
            
        return False


    @staticmethod
    def submit(form_args):
        patient_uuid = form_args['patient_uuid']        
        location_uuid = form_args['location_uuid']        
        provider_uuid = form_args['provider_uuid']
        encounter_type_uuid = form_args['encounter_type_uuid']
        encounter_datetime = form_args['encounter_datetime']
        
        obs = EncounterForm.get_obs(form_args)
        if EncounterForm.is_duplicate(patient_uuid,encounter_datetime,location_uuid,encounter_type_uuid,provider_uuid,obs):
            print 'ERROR: this form has already been submitted'
            return None

        rest_log = Encounter.create_encounter_rest(patient_uuid=patient_uuid,
                                                   encounter_datetime=encounter_datetime,
                                                   location_uuid=location_uuid,
                                                   encounter_type_uuid=encounter_type_uuid,
                                                   provider_uuid=provider_uuid,
                                                   obs=obs)
        return rest_log


    @staticmethod
    def process_encounter(form_args,creator):
        log = ""
        try:
            patient_uuid = form_args['patient_uuid']        
            print "process_encounter() : " + str(form_args['location_uuid'])

            location_uuid = form_args['location_uuid']
            provider_uuid = form_args['provider_uuid']
            encounter_type_uuid = form_args['encounter_type_uuid']
            encounter_datetime = form_args['encounter_datetime']

            rest_log = EncounterForm.submit(form_args)
            #rest_log is None when the encounter is a duplicate
            print "process_encounter()"
            print rest_log

            if rest_log :
                log = EncounterLog.log(creator,patient_uuid,encounter_type_uuid,encounter_datetime,rest_log.id)
                EncounterForm.set_person_attributes(form_args)
                EncounterForm.set_dead(form_args)
        except Exception,e:
            print "Exception: " + str(e)
            print str(form_args)
        return log



    @staticmethod
    def reprocess_encounter(log_id,form_args):
        log = EncounterLog.objects.get(id=log_id)
        rest_log = RESTLog.objects.get(id=log.rest_log_id)
        rest_log.retire()

        rest_log = EncounterForm.submit(form_args)
        log.id=rest_log.id
        log.save()
        EncounterForm.set_dead(form_args)



class EncounterLog(models.Model):
    patient_uuid = models.CharField(max_length=50,db_index=True)
    encounter_type_uuid = models.CharField(max_length=500)
    encounter_datetime = models.DateTimeField()
    rest_log_id = models.IntegerField()
    creator = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def log(creator,patient_uuid,encounter_type_uuid,encounter_datetime,rest_log_id):
        log = EncounterLog(creator=creator,
                           patient_uuid=patient_uuid,
                           encounter_type_uuid=encounter_type_uuid,                           
                           encounter_datetime=encounter_datetime,
                           rest_log_id=rest_log_id)
        log.save()
        return log


    def resubmit(self):
        log = RESTLog.objects.get(id=self.rest_log_id)
        if log.result_uuid is None :
            log = RESTHandler.repost(log)            
        return log


    def get_patient_name(self):
        p = Patient.get_patient_by_uuid(self.patient_uuid)
        name = p['given_name'] + ' ' + p['middle_name'] + ' ' + p['family_name']
        return name


    def get_form_vals(self):
        rest_log = RESTLog.objects.get(id=self.rest_log_id)
        vals = json.loads(rest_log.payload)
        form_vals = {'patient_uuid':vals['patient'],
                     'encounter_datetime':vals['encounterDatetime'],
                     'encounter_type_uuid':vals['encounterType'],
                     'provider_uuid':vals['provider'],
                     'location_uuid':vals['location'],
                     }
                
        print vals['obs']
        obs = []
        for o in vals['obs']:            
            question = Concept.get_concept_info(o['concept'])            
            question['answer'] = o['value']
            obs.append(question)
                
        form_vals['obs'] = obs

        return form_vals



class OutreachForm(EncounterForm):

    @staticmethod
    def process_outreach_form(args,user_id):
        EncounterForm.process_encounter(args)
        
        dcm_id = args.get('defaulter_cohort_member_id',None)
        if dcm_id is not None and dcm_id != '' and dcm_id != 'None':
            log.defaulter_cohort_member_id = dcm_id
            log.save()
            
            member = DefaulterCohortMember.objects.get(id=dcm_id)
            args = {'next_appt_date':encounter_datetime,
                    'next_encounter_type':"OUTREACHFIELDFU",
                    }
            member.update_status(args)


