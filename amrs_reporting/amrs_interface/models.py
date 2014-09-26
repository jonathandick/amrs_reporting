from django.db import models
import MySQLdb as mdb
import report.settings as settings
from report.models import *
from utilities import *
import requests
import json
import amrs_settings

class Location(models.Model):

    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE
    

    @staticmethod
    def get_all(retired=0):
        print 'get_all() .......'
        locations = {}
        con = None        
        try :
            sql = 'select location_id, name from amrs.location where retired=' + str(retired) + ' order by name'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            locations = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()
        
        return locations


    @staticmethod
    def get_names(retired=0,subset=None):
        names = {}
        con = None
        try :
            sql = 'select name from amrs.location where retired=' + str(retired)
            if subset: sql += ' and location_id in ' + subset
            sql += ' order by name'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            names = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()
        return names




    @staticmethod
    def get_locations(location_ids=None):
        locations = {}
        con = None
        try :
            sql = 'select location_id, name,uuid from amrs.location'
            if location_ids : 
                location_ids = ','.join(str(x) for x in location_ids)
                sql += ' where location_id in (' + location_ids + ')'
            sql += ' order by name'
            print sql
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            locations = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return locations


    @staticmethod
    def get_location(location_id) :
        location = {}
        con = None
        try :
            sql = 'select location_id, name, uuid from amrs.location where location_id=%s'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(location_id,))
            location = cur.fetchone()
        except Exception, e:
            print e
            
        finally:
            if con : con.close()

        return location

    @staticmethod
    def get_location_by_uuid_db(location_uuid) :
        location = {}
        con = None
        try :
            sql = 'select location_id, name, uuid from amrs.location where uuid=%s'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(location_uuid,))
            location = cur.fetchone()
        except Exception, e:
            print e
            
        finally:
            if con : con.close()

        return location



    @staticmethod
    def get_location_by_uuid(location_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/location/' + location_uuid
        location = ''
        try:
            res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
            data = json.dumps(res.text)            
            location = {'name':data['name'],
                        'uuid':data['uuid']}
        except:
            pass
        return location


class Person():

    @staticmethod
    def set_dead(person_uuid,death_date,cause_of_death):
        try:
            headers = {'content-type': 'application/json','connection':'close'}
            url = amrs_settings.amrs_url + '/ws/rest/v1/person/' + person_uuid    
            payload = {'deathDate':death_date,
                       'dead':'true',
                       'causeOfDeath':cause_of_death,
                       }
            data = json.dumps(payload)
            res = requests.post(url,data,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)        
            return json.loads(res.text)
        except Exception, e:
            return 'error'


class Patient():

    @staticmethod
    def search_patients(search_string):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/patient?v=default&limit=20&q=' + search_string
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        data = json.loads(res.text)['results']
        patients = []
        for p in data:
            ids = p['identifiers']
            identifiers = ''
            for i in ids:
                parts = i['display'].split(' = ')
                identifiers += parts[1] + '; '
            patient_uuid = p['uuid']
            names = p['person']['display']
            split = names.split(' ')
            num_names = len(split)
            given_name = split[0]
            family_name = split[-1]
            middle_name = ''
            for x in range(1,num_names-1):
                middle_name += split[x] + ' '
        
            gender = p['person']['gender']
            birthdate = p['person']['birthdate']
            birthdate = birthdate.split('T')[0]
            phone_number = ''
            
            for a in p['person']['attributes']:
                if a['display'].startswith('Contact Phone Number'):
                    split = a['display'].split(' = ')
                    phone_number += split[1] + ' '
                
            

            patient = {'given_name':given_name,
                       'middle_name':middle_name,
                       'family_name':family_name,
                       'identifier':identifiers,
                       'gender':gender,
                       'birthdate':birthdate,
                       'uuid':patient_uuid,
                       'phone_number':phone_number
                       }
            patients.append(patient)
        res.close()
        return patients
        

    @staticmethod
    def get_patient_by_uuid(patient_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/patient/' + patient_uuid
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        data = json.loads(res.text)
        names = data['person']['display']
        split = names.split(' ')
        num_names = len(split)
        given_name = split[0].title()
        family_name = split[num_names-1].title()
        middle_name = ''
        for x in range(1,num_names-1):
            middle_name += ' ' + split[x].title()
        
        identifier = data['identifiers'][0]['display']
        split = identifier.split(' = ')
        identifier = split[1]

        gender = data['person']['gender']
        birthdate = data['person']['birthdate']

        phone_number = ''

        for a in data['person']['attributes']:
            if a['display'].startswith('Contact Phone Number'):
                split = a['display'].split(' = ')
                phone_number += split[1] + ' '
        

        patient = {'given_name':given_name,
                   'middle_name':middle_name,
                   'family_name':family_name,
                   'identifier':identifier,
                   'gender':gender,
                   'birthdate':birthdate,
                   'uuid':patient_uuid,
                   'phone_number':phone_number
                   }
        return patient
    


                       
class Provider(models.Model):
        
    @staticmethod
    def get_outreach_providers():
        providers = {}
        con = None
        try :
            sql = 'select t2.identifier, given_name, family_name, t4.uuid'
            sql += ' from flat_outreach_data t1'
            sql += ' join amrs.provider t2 using (provider_id)'
            sql += ' join amrs.person_name t3 on t2.person_id=t3.person_id'
            sql += ' join amrs.person t4 on t2.person_id=t4.person_id'
            sql += ' where t1.encounter_datetime >= "2014-01-01"'
            sql += ' group by t2.identifier order by given_name, family_name'

            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            providers = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return providers


    @staticmethod
    def get_provider_name(provider_id) :
        provider = {}
        con = None
        try :
            sql = 'select person_id as provider_id,given_name,family_name from amrs.person_name where person_id=% and voided=0'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(provider_id,))
            location = cur.fetchone()
        except Exception, e:
            print e
            
        finally:
            if con : con.close()

        return provider


    @staticmethod
    def get_outreach_worker_indicators(provider_id):
        rt = ReportTable.objects.filter(name='outreach_worker_indicators')[0]
        outreach_worker_indicators = rt.run_report_table(as_dict=True)['rows']
        return outreach_worker_indicators


class Concept():

    @staticmethod
    def is_valid_concept_uuid(concept_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/concept/' + concept_uuid
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        data = json.loads(res.text)
        #print 'Error: ' + str('error' in data)        
        return ('error' not in data)
        
        


class EncounterType():

    @staticmethod
    def get_encounter_type_by_uuid(uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/encountertype/' + uuid
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        data = json.loads(res.text)
        name = data['name']
        description = data['description']
        return {'name':name,
                'description':description,
                'uuid':uuid,
                }
    
        

class Encounter():
    @staticmethod
    def create_encounter_rest(patient_uuid=None, encounter_datetime=None,encounter_type_uuid=None,provider_uuid=None,location_uuid=None,obs=[]):
        import datetime
        headers = {'content-type': 'application/json'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter'    
        payload = {'patient':patient_uuid,
                   'encounterDatetime':encounter_datetime,               
                   'location':location_uuid,
                   'encounterType':encounter_type_uuid,
                   'provider':provider_uuid,
                   'obs': obs
                   }
        data = json.dumps(payload)
        #print data
        res = requests.post(url,data,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        return json.loads(res.text)



    @staticmethod
    def get_last_encounter(patient_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter?patient=' + patient_uuid + '&limit=1'
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        vals = json.loads(res.text)['results'][0]
        print vals

        enc_uuid = vals['uuid']

        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter/' + enc_uuid
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)

        vals = json.loads(res.text)

        encounter_type = vals['encounterType']['display']
        encounter_datetime = vals['encounterDatetime']
 
        rtc_date = ''
        obs = []
        for o in vals['obs'] :
            if o['uuid'] == 'a8a666ba-1350-11df-a1f1-0026b9348838':
                split = o['display'].split(' : ')
                obs.append({'question': split[0],'answer':split[1]})
        enc = {'uuid':enc_uuid,
               'encounter_type':encounter_type,
               'encounter_datetime':encounter_datetime,
               'obs':obs
               }
        return enc


        

    @staticmethod
    def get_last_encounter_db(patient_uuid):

        encounter = {}
        con = None
        try :
            sql = 'select encounter_datetime, name as encounter_type, rtc_date'
            sql += ' from reporting_JD.flat_retention_data t1 join amrs.encounter_type t2 on t1.encounter_type = t2.encounter_type_id'
            sql += ' where t1.uuid=%s and next_appt_date is NULL'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(patient_uuid,))
            encounter = cur.fetchone()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return encounter


    @staticmethod 
    def get_last_date_created_db(location_id):
        encounter = {}
        con = None
        try :
            sql = 'select max(enc_date_created) as date_created'
            sql += ' from reporting_JD.flat_retention_data t1'
            sql += ' where t1.location_id=%s'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(location_id,))
            encounter = cur.fetchone()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return encounter['date_created']

        
    @staticmethod
    def get_encounters(patient_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter?patient=' + patient_uuid
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        data = json.loads(res.text)['results']
        encounters = []
        for r in data:
            parts = r['display'].split(' ')
            d = parts[1].split('/')
            if len(d) == 3 :
                encounter_date = d[2]+'/'+d[1]+'/'+d[0]
            else : encounter_date = ''
            encounter = {'encounter_date': encounter_date,
                         'encounter_type':parts[0],
                         }
            encounters.append(encounter)
            
        return list(reversed(encounters))
            
            

class RetentionDataset():
    
    @staticmethod
    def get_sync_stats():
        con = None
        results = {}
        try :
            sql = 'select count(*) as retention_count, max(enc_date_created) as retention_max from reporting_JD.flat_retention_data'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            row = cur.fetchone()
            results['retention_max'] = row['retention_max']
            results['retention_count'] = row['retention_count']

            print results
            sql = 'select count(*) as encounter_count, max(date_created) as encounter_max from amrs.encounter where voided=0'
            sql += ' and encounter_type in (1,2,3,4,10,13,14,15,17,19,22,23,26,43,47,21)'            
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            row = cur.fetchone()
            results['encounter_max'] = row['encounter_max']
            results['encounter_count'] = row['encounter_count']
            print results
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return results
        



    @staticmethod
    def get_encounter(encounter_id):
        encounter = {}
        con = None
        try :
            sql = 'select * from flat_retention_data where encounter_id = %s'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(encounter_id,))
            encounter = cur.fetchone()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return encounter
        

    @staticmethod
    def get_encounters(encounter_ids=[]):
        encounters = []
        con = None
        try :
            sql = 'select * from flat_retention_data where encounter_id in %s'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(tuple(encounter_ids),))
            encounters = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return encounters


    @staticmethod
    def get_last_clinic_location_id(patient_uuid):
        location_id = ""
        con = None        
        try :
            sql = 'select location_id from flat_retention_data where uuid = %s and next_appt_date is null'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(patient_uuid,))
            location_id = cur.fetchone()['location_id']  
            
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return location_id


class PersonAttribute():

    @staticmethod
    def create_person_attribute_rest(person_uuid=None,person_attribute_type_uuid=None,value=None,void_existing=True):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/person/' + person_uuid + '/attribute'    

        if void_existing :
            res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),verify=False)
            vals = json.loads(res.text)['results']
            for v in vals:
                type_uuid = v['attributeType']['uuid']
                uuid = v['uuid']
                if type_uuid == person_attribute_type_uuid :
                    requests.post(url + '/' + uuid + '?!purge',auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
            

        payload = {'attributeType':person_attribute_type_uuid,
                   'value':value
                   }
        data = json.dumps(payload)
        res = requests.post(url,data,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        return json.loads(res.text)



class Cohort(models.Model):

    url_cohort = amrs_settings.amrs_url + '/ws/rest/v1/cohort/' 


    @staticmethod
    def create_cohort(name=None,description=None,patient_uuids=[]):
        headers = {'content-type': 'application/json','connection':'close'}
        payload = {'name': name,
                   'description': description,
                   'memberIds':patient_uuids,
                   }
        data = json.dumps(payload)
        req = requests.post(Cohort.url_cohort, data, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        vals = json.loads(req.text)
        if 'error' in vals:
            print 'error creating new cohort'
            return 'error'
            
        return vals['uuid']

    @staticmethod
    def delete_cohort_members(cohort_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        if cohort_uuid is not None and cohort_uuid != '':
            Cohort.url_cohort += cohort_uuid + '/member'
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
        


    @staticmethod
    # this removes all current members of a cohort and adds the provided patient_uuids
    def update_cohort_members(cohort_uuid=None,patient_uuids=None):
        headers = {'content-type': 'application/json','connection':'close'}
        Cohort.remove_members(patient_uuids)
        for uuid in patient_uuids:
            payload = {'patient':uuid}
            data = json.dumps(payload)
            req = requests.post(Cohort.url_cohort, data, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        
   
    
    @staticmethod
    def delete_cohort(cohort_uuid):
        url = Cohort.url_cohort + '/' + cohort_uuid
        headers = {'content-type': 'application/json','connection':'close'}
        req = requests.delete(url, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        

    @staticmethod
    def delete_cohort_member(cohort_uuid,patient_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        if cohort_uuid is not None and cohort_uuid != '':
            url = Cohort.url_cohort + '/' + cohort_uuid + '/member/' + patient_uuid
            req = requests.delete(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
                   


    @staticmethod
    def get_member_uuids(cohort_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        uuids = []
        if cohort_uuid is not None and cohort_uuid != '':
            Cohort.url_cohort += cohort_uuid + '/member'
            req = requests.get(url_cohort + '?v=ref', auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
            vals = json.loads(req.text)

            for member in vals['results']:                
                parts = member['links'][0]['uri'].split('member/')
                uuids.append(parts[1])
        return uuids




    @staticmethod
    def get_patients(cohort_uuid):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/cohort/' + cohort_uuid + '/member?v=full'
        res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        data = json.loads(res.text)['results']
        patients = []
        for member in data:
            p = member['patient']

            ids = p['identifiers']
            identifiers = ''
            for i in ids:
                parts = i['display'].split(' = ')
                identifiers += parts[1] + '; '
            patient_uuid = p['uuid']
            names = p['person']['display']
            split = names.split(' ')
            num_names = len(split)
            given_name = split[0]
            family_name = split[-1]
            middle_name = ''
            for x in range(1,num_names-1):
                middle_name += ' ' + split[x]
        
            gender = p['person']['gender']
            birthdate = p['person']['birthdate']
            birthdate = birthdate.split('T')[0]
            phone_number = ''
            
            for a in p['person']['attributes']:
                if a['display'].startswith('Contact Phone Number'):
                    split = a['display'].split(' = ')
                    phone_number += split[1] + ' '
                
            

            patient = {'given_name':given_name,
                       'middle_name':middle_name,
                       'family_name':family_name,
                       'identifier':identifiers,
                       'gender':gender,
                       'birthdate':birthdate,
                       'uuid':patient_uuid,
                       'phone_number':phone_number
                       }
            patients.append(patient)
        return patient
        
        

class DerivedGroup(models.Model):
    
    name = models.CharField(max_length=200)
    base_class = models.CharField(max_length=200)

    description = models.CharField(max_length=500)


    def get_base_members(self):
        return (globals()[self.base_class]).get_all()


    def get_base_class(self):
        return globals()[self.base_class]
        

    def is_member(self,member_id):
        members = DerivedGroupMember.objects.filter(id=self.id,member_id=member_id)
        return len(members) > 0


    def get_members(self):
        return DerivedGroupMember.objects.filter(derived_group_id=self.id)
    
    def get_member_ids(self):
        return DerivedGroupMember.objects.filter(derived_group_id=self.id).values_list('member_id',flat=True)

    def get_member_names(self):
        c = self.get_base_class()
        ids = self.get_member_ids()
        ids = '(' + ','.join(str(id) for id in ids) + ')'
        return c.get_names(subset=ids)
        


    def set_self(self,args):
        name = get_var(args,'name')
        base_class = get_var(args,'base_class')
        description = get_var(args,'description')
        members = args.getlist('members')
        member_ids = get_var(args,'member_ids')

        if name and base_class and (members or member_ids):
            self.name = name
            self.base_class = base_class
            self.description = description
            self.save()
            
            DerivedGroupMember.objects.filter(derived_group_id=self.id).delete()
            if member_ids :
                member_ids = member_ids.replace(' ','').split(',')
            else : member_ids = members
            
            for member_id in member_ids :
                dg = DerivedGroupMember(derived_group_id=self.id,member_id=member_id)
                dg.save()

                    

class DerivedGroupMember(models.Model):
    derived_group_id = models.IntegerField()
    member_id = models.IntegerField()
    
