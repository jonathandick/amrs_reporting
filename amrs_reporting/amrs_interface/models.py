from django.db import models
import MySQLdb as mdb
import report.settings as settings
from report.models import *
from utilities import *
import requests
import json
import amrs_settings

class RESTHandler():

    headers = {'content-type': 'application/json','connection':'close'}        

    @staticmethod
    def get(url):
        try :
            print "REST: do GET : " + str(url)
            res = requests.get(url,auth=(amrs_settings.username,amrs_settings.password),headers=RESTHandler.headers,verify=False)
            result = json.loads(res.text)
            res.close()
        except Exception, e:
            print 'exception: ' + str(e)
            result = {'error':{'message':e}}
        return result
        

    @staticmethod
    def post(url,payload):
        print "REST: do POST : " + str(url)
        try :
            res = requests.post(url,payload,auth=(amrs_settings.username,amrs_settings.password),headers=RESTHandler.headers,verify=False)
            result = json.loads(res.text)
            e = result.get('error',None)
            if e :
                print 'REST URL leading to error: ' + url
                s = e['detail'].split('\\n\\tat')
                for line in s:
                    print line
            res.close()
        except Exception, e:
            result = {'error':{'message':e}}
        return result
    

    @staticmethod
    def post_and_log(url,payload):
        payload = json.dumps(payload)
        result = RESTHandler.post(url,payload)
        log = RESTLog.log(url,payload,result)
        return log



    @staticmethod
    def repost(log=None,log_id=None):
        if log is None :
            log = RESTLog.objects.get(id=log_id)

        result = RESTHandler.post(log.url,log.payload)
        if result.get('error',None) :
            log.error = result.get('error')
        else :
            log.error = ''
            log.result_uuid = result['uuid']
        log.save()
        return log


    '''
    Convenience method to repost all non-retired errors. For unclear reasons, AMRS is throwing exceptions which
    later do not occur using the same data.
    '''
    @staticmethod
    def repost_errors():
        logs = RESTLog.objects.filter(retired=0).exclude(error='')        
        for log in logs:
            l = RESTHandler.repost(log.id)
            


class RESTLog(models.Model):
    url = models.CharField(max_length=1000)
    payload = models.TextField()
    result_uuid = models.CharField(max_length=500,null=True)
    error = models.TextField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    last_date_updated = models.DateTimeField(auto_now=True)

    retired = models.BooleanField(default=False)
    date_retired = models.DateTimeField(null=True)


    @staticmethod
    def log(url,payload,result):                
        log = RESTLog(url=url,
                      payload=payload)
                            
        if result.get('error',None) : 
            log.error = str(result['error']['message'])
        else :
            log.result_uuid = result['uuid']
            

        log.save()
        return log


    def retire(self):
        from datetime import datetime
        self.retired = True
        self.date_retired = datetime.today()
        self.save()



class OpenmrsSession(models.Model):
    
    @staticmethod
    def authenticate(username,password) :
        headers = {'content-type': 'application/json','connection':'close'}        
        try :
            url = amrs_settings.amrs_url + '/ws/rest/v1/session'
            res = requests.get(url,auth=(username,password),headers=headers,verify=False)
            result = json.loads(res.text)
            res.close()
            if 'authenticated' in result : return result['authenticated']
            else : return False 
        except Exception, e:
            print 'exception: ' + str(e)
            result = {'error':{'message':e}}
            
        return False 

    


class Location(models.Model):

    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE
    

    @staticmethod
    def get_all(retired=0):
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
            #death_date = "2014-05-10T00:00:00.000+0300"
            payload = {'deathDate':death_date,
                       'dead':'true',
                       'causeOfDeath':cause_of_death,
                       }
            data = json.dumps(payload)

            res = requests.post(url,data,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)        
            result = json.loads(res.text)
            res.close()
            print 'deathDate: ' + str(death_date)
            if result.get("error") : print result["error"]["detail"][0:200]
            return result

            '''
            log = RESTHandler.post_and_log(user_id,url,payload,'person')
            return log
            '''

        except Exception, e:
            return 'error'


class Patient():

    @staticmethod
    def search_patients(search_string):
        url = amrs_settings.amrs_url + '/ws/rest/v1/patient?v=default&limit=20&q=' + search_string
        result = RESTHandler.get(url)
    
        data = result.get('results',None)
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
        return patients
        

    @staticmethod
    def get_patient_by_uuid(patient_uuid):
        url = amrs_settings.amrs_url + '/ws/rest/v1/patient/' + patient_uuid 
        #url += '?v=custom:(uuid,person:(uuid,gender,birthdate,preferredName:(givenName,middleName,familyName),birthdate),identifiers:(identifier)'
        data = RESTHandler.get(url)
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
                   'phone_number':phone_number,
                   }
        return patient
    

    '''
    obs_info : {"name":"name",concept_id:123n,"uuid":"uuid"
    container
    combine : put all concepts into one column
    '''
    @staticmethod
    def get_obs_data_pretty(patient_uuid,obs_info,container,combine=False,combine_column_name=None) :
        
        obs_url = amrs_settings.amrs_url + '/ws/rest/v1/obs?patient=' + patient_uuid
        c_url = obs_url + "&concept=" + obs_info["uuid"]
        c_url += "&v=custom:(uuid,obsDatetime,encounter:(uuid,encounterDatetime),value:(uuid,name:(name,uuid),uuid),concept:(uuid,name:(name)))"
        data = RESTHandler.get(c_url)
        
        for o in data['results'] :                
            e = o.get("encounter",None)
            
            if e : encounter_datetime = o["encounter"]['encounterDatetime']                    
            else :  
                encounter_datetime = str(o['obsDatetime']) + " - lab"                    
            
            value = o['value']
            if isinstance(value,dict) : value = o['value']['name']['name']                
            value = str(value).title()

            col_name = obs_info['name']
            if combine : 
                col_name = combine_column_name
                value = obs_info['name'].title() + " = " + value

            if encounter_datetime in container : 
                if col_name in container[encounter_datetime]['obs'] :
                    container[encounter_datetime]['obs'][col_name].append(value)
                else : 
                    container[encounter_datetime]['obs'][col_name] = [value]
            else : container[encounter_datetime] = {"encounter_datetime":encounter_datetime,"obs":{col_name:[value]}}
        return container

        

    @staticmethod
    def get_encounter_data(patient_uuid):
        url = amrs_settings.amrs_url + '/ws/rest/v1/patient/' + patient_uuid 
                
        encounters = {}
        encounter_url = amrs_settings.amrs_url + '/ws/rest/v1/encounter?patient=' + patient_uuid         
        encounter_url += "&v=custom:(uuid,location:(uuid,name),dateCreated,encounterDatetime,encounterType:(uuid,name),provider)&limit=200"
        data = RESTHandler.get(encounter_url)
        for e in data['results']:            
            provider_name = e["provider"]["display"]
            encounter = {"uuid":e["uuid"],
                         "encounter_datetime":e["encounterDatetime"],
                         "provider": provider_name,
                         "encounter_type":e["encounterType"]["name"].title(),
                         "location":e["location"]["name"].title(),
                         "obs":{},
                         }
            encounters[str(e["encounterDatetime"])] = encounter
            
                         

        core_concepts = [
            {"name":"WEIGHT (KG)","concept_id":5089,"uuid":"a8a660ca-1350-11df-a1f1-0026b9348838"},
            {"name":"ANTIRETROVIRAL PLAN","concept_id":1255,"uuid":"a89b75d4-1350-11df-a1f1-0026b9348838"},
            {"name":"ANTIRETROVIRALS STARTED","concept_id":1250,"uuid":"a89b6a62-1350-11df-a1f1-0026b9348838"},
            {"name":"CURRENT ANTIRETROVIRAL DRUGS USED FOR TREATMENT","concept_id":1088,"uuid":"a899cf5e-1350-11df-a1f1-0026b9348838"},
            {"name":"PROBLEM ADDED","concept_id":6042,"uuid" : "a8ae835e-1350-11df-a1f1-0026b9348838"},
            {"name":"RETURN VISIT DATE","concept_id":5096,"uuid" : "a8a666ba-1350-11df-a1f1-0026b9348838"},
            {"name":"MEDICATION ADDED","concept_id":1895,"uuid" : "a8a060c6-1350-11df-a1f1-0026b9348838"},
            {"name":"PCP Prophylaxis","concept_id":1109,"uuid" : "a899e282-1350-11df-a1f1-0026b9348838"},
            {"name":"TESTS ORDERED","concept_id":1271,"uuid":"a89c2268-1350-11df-a1f1-0026b9348838"},                    
            {"name":"CD4, BY FACS","concept_id":5497,"uuid":"a8a8bb18-1350-11df-a1f1-0026b9348838"},
            {"name":"HIV VIRAL LOAD, QUANTITATIVE","concept_id":856, "uuid":"a8982474-1350-11df-a1f1-0026b9348838"},
            {"name":"MEDICATION ORDERS","concept_id":1895, "uuid":"a8a060c6-1350-11df-a1f1-0026b9348838"},
            ]

        lab_concepts = [
            {"name":"HEMOGLOBIN","concept_id":21,"uuid" : "a8908a16-1350-11df-a1f1-0026b9348838"},
            {"name":"WBC","concept_id":678,"uuid" : "a896dea2-1350-11df-a1f1-0026b9348838"},
            {"name":"SGPT","concept_id":654,"uuid" : "a896ca48-1350-11df-a1f1-0026b9348838"},                    
            {"name":"Cr","concept_id":790,"uuid" : "a897e450-1350-11df-a1f1-0026b9348838"},                    
            {"name":"SPUTUM FOR AFB","concept_id":307,"uuid" : "a8945d4e-1350-11df-a1f1-0026b9348838"},
            {"name":"Gene xpert","concept_id":8070,"uuid" : "741517cf-8bac-4755-b289-8dd2a2df7962"},            
            ]

        tb_concepts = [
            {"name":"TB Prophylaxis","concept_id":1110,"uuid" : "a899e35e-1350-11df-a1f1-0026b9348838"},
            {"name":"TB Prophylaxis Plan","concept_id":1265,"uuid" : "a89c1cfa-1350-11df-a1f1-0026b9348838"},
            {"name":"TB Prophylaxis Stop Reason","concept_id":1266,"uuid" : "a89c1e12-1350-11df-a1f1-0026b9348838"},
            {"name":"TB Tx Start Date","concept_id":1113,"uuid" : "a899e5f2-1350-11df-a1f1-0026b9348838"},
            {"name":"Current TB Meds","concept_id":1111,"uuid" : "a899e444-1350-11df-a1f1-0026b9348838"},
            {"name":"TB tx Plan","concept_id":1268,"uuid" : "a89c1fd4-1350-11df-a1f1-0026b9348838"},
            {"name":"Start Reason","concept_id":6981,"uuid" : "749d07cb-4994-4ce9-a39c-8a655a487fdd"},
            {"name":"Stop/Change Reason","concept_id":1269,"uuid" : "749d07cb-4994-4ce9-a39c-8a655a487fdd"},
            {"name":"New TB Drugs","concept_id":1270,"uuid" : "a89c218c-1350-11df-a1f1-0026b9348838"},
            ]

        core_data = encounters
        for c in core_concepts :
            core_data = Patient.get_obs_data_pretty(patient_uuid,c,core_data)

        for c in lab_concepts :
            core_data = Patient.get_obs_data_pretty(patient_uuid,c,core_data,combine=True,combine_column_name="LAB RESULTS")

        tb_data = {}
        for c in tb_concepts :
            tb_data = Patient.get_obs_data_pretty(patient_uuid,c,tb_data)
    
        data = {"core":core_data,
                "tb":tb_data,
                }
        return data

        

                       
class Provider(models.Model):
        
    @staticmethod
    def get_outreach_providers():
        providers = {}
        con = None
        try :
            sql = 'select t3.identifier, given_name, family_name, t5.uuid'
            sql += ' from flat_outreach_defined t1'
            sql += ' join flat_retention_defined t2 using (encounter_id)'
            sql += ' join amrs.provider t3 using (provider_id)'
            sql += ' join amrs.person_name t4 on t3.person_id=t4.person_id'
            sql += ' join amrs.person t5 on t3.person_id=t5.person_id'
            sql += ' where t2.encounter_datetime >= "2014-01-01"'
            sql += ' group by t3.identifier order by given_name, family_name'

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
        url = amrs_settings.amrs_url + '/ws/rest/v1/concept/' + concept_uuid
        result = RESTHandler.get(url)
        return ('error' not in result)


    @staticmethod
    def get_concept_info(concept_uuid):
        url = amrs_settings.amrs_url + '/ws/rest/v1/concept/' + concept_uuid
        data = RESTHandler.get(url)
        concept = {}
        concept['name'] = data['display']
        concept['datatype'] = data['datatype']['display']
        concept['uuid'] = data['uuid']

        answers = []
        for a in data['answers']:
            answer = {'uuid':a['uuid'],
                      'name':a['display'],
                      }
            answers.append(answer)

        concept['answers'] = answers
        return concept
        

    @staticmethod
    def search_concepts(search_string):
        url = amrs_settings.amrs_url + '/ws/rest/v1/concept?v=default&limit=50&q=' + search_string
        result = RESTHandler.get(url)
        data = result.get('results',None)        
        try :
            concepts = []
            for c in data:
                concept = {'name':c['display'].capitalize(),
                           'uuid':c['uuid']}
                concepts.append(concept)
        except Exception, e:
            print e

        return concepts

    


class EncounterType():

    @staticmethod
    def get_encounter_type_by_uuid(uuid):
        url = amrs_settings.amrs_url + '/ws/rest/v1/encountertype/' + uuid
        data = RESTHandler.get(url)
        name = data['name']
        description = data['description']
        return {'name':name,
                'description':description,
                'uuid':uuid,
                }


    @staticmethod
    def get_encounter_types():
        encounter_types = {}
        con = None
        try :
            sql = 'select * from amrs.encounter_type'
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            encounter_types = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return encounter_types

        
    
        

class Encounter():
    @staticmethod
    def create_encounter_rest(patient_uuid=None, encounter_datetime=None,encounter_type_uuid=None,provider_uuid=None,location_uuid=None,form_uuid="",obs=[]):
        import datetime
        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter'    
        payload = {'patient':patient_uuid,
                   'encounterDatetime':encounter_datetime,               
                   'location':location_uuid,
                   'encounterType':encounter_type_uuid,
                   'provider':provider_uuid,
                   'form':form_uuid,
                   'obs': obs
                   }

        
        log = RESTHandler.post_and_log(url,payload)

        #headers = {'content-type': 'application/json','connection':'close'}
        #data = json.dumps(payload)
        #res = requests.post(url,data,auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        #result = json.loads(res.text)
        #res.close()
        return log



    @staticmethod
    def get_last_encounter(patient_uuid):
        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter?patient=' + patient_uuid + '&limit=1'        
        result = RESTHandler.get(url)
        vals = results['results'][0]

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
        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter?patient=' + patient_uuid
        url += '&v=custom:(uuid,encounterType:(uuid,name),encounterDatetime,location:(uuid,name))'
        result = RESTHandler.get(url)
        data = result['results']
        return data
            

    @staticmethod
    def get_encounter(uuid):        
        url = amrs_settings.amrs_url + '/ws/rest/v1/encounter/' + uuid
        url += '?v=custom:(location:(uuid,name),encounterDatetime,encounterType:(uuid,name),provider,obs:ref)'
        result = RESTHandler.get(url)
        encounter = {"encounterDatetime":result.get("encounterDatetime","")}
        if(result.get("encounterType")) : encounter["encounterType"] = result.get("encounterType")["name"]
        if(result.get("provider")) : encounter["provider"] = result.get("provider")["display"]
        if(result.get("location")) : encounter["location"] = result.get("location")["name"]
        if(result.get("obs")) :
            obs = {}
            for o in result.get("obs") :
                parts = o["display"].split(": ")
                obs[parts[0]] = parts[1]
            encounter['obs'] = obs
        return encounter
        
        
            

                     
        
            

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

            sql = 'select count(*) as encounter_count, max(date_created) as encounter_max from amrs.encounter where voided=0'
            sql += ' and encounter_type in (1,2,3,4,10,13,14,15,17,19,22,23,26,43,47,21)'            
            con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            row = cur.fetchone()
            results['encounter_max'] = row['encounter_max']
            results['encounter_count'] = row['encounter_count']
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
    def get_patient_encounters(patient_uuid=None,person_id=None,order_by='encounter_datetime desc'):
        encounters = []
        con = None
        try :
            sql = None
            if patient_uuid :
                id = patient_uuid
                sql = 'select * from flat_retention_data where uuid=%s order by ' + order_by
            elif person_id :
                id = person_id
                sql = 'select * from flat_retention_data where person_id=%s order by ' + order_by
            if sql :
                con = mdb.connect(settings.HOST,settings.USER,settings.PASSWORD,settings.DATABASE)
                cur = con.cursor(mdb.cursors.DictCursor)
                cur.execute(sql,(id,))
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
        '''
        if void_existing :
            result = RESTHandler.get(url)
            print result
            vals = result['results']
            for v in vals:
                type_uuid = v['attributeType']['uuid']
                uuid = v['uuid']
                if type_uuid == person_attribute_type_uuid :
                    purge_url = url + '/' + uuid + '?!purge'
                    RESTHandler.post(purge_url,[])                    
            
        '''
        payload = {'attributeType':person_attribute_type_uuid,
                   'value':value
                   }        
        log = RESTHandler.post_and_log(url,payload)
        return log


    @staticmethod
    def test_hydrated(person_uuid=None,person_attribute_type_uuid=None,value=None,void_existing=True):
        headers = {'content-type': 'application/json','connection':'close'}
        url = amrs_settings.amrs_url + '/ws/rest/v1/person/' + person_uuid + '/attribute'
        payload = {'attributeType':person_attribute_type_uuid,
                   'hydratedObject':value
                   }
        log = RESTHandler.post_and_log(url,payload)
        return log



class Cohort():

    url_cohort = amrs_settings.amrs_url + '/ws/rest/v1/cohort/' 


    @staticmethod
    def create_cohort(name=None,description=None,patient_uuids=[]):
        headers = {'content-type': 'application/json','connection':'close'}
        payload = {'name': name,
                   'description': description,
                   'memberIds':patient_uuids,
                   }
        data = json.dumps(payload)
        res = requests.post(Cohort.url_cohort, data, auth=(amrs_settings.username,amrs_settings.password),headers=headers,verify=False)
        vals = json.loads(res.text)
        if 'error' in vals:
            print 'error creating new cohort'
            return 'error'

        res.close()
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
            req.close()


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
    








    
