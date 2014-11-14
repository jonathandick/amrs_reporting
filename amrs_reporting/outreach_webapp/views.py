from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.serializers.json import DjangoJSONEncoder
import pytz
from datetime import datetime, date

from utilities import *
from defaulter_cohort.models import *
from encounter_form.models import *
from amrs_interface.models import *
from amrs_user_validation.models import Authorize
from outreach_webapp.models import *
import base64


def ajax_auth(request):
    if str(request.user) != "AnonymousUser" :
        return request.user.is_authenticated()

    else:
        if request.method == "OPTIONS":             
            print 'method is OPTIONS : purpose is for preflight. will authenticate for now'
            return True
            
        encoded_auth_info = request.META.get("HTTP_AUTHORIZATION")
        if encoded_auth_info is not None : 
            auth_info = base64.decodestring(encoded_auth_info.replace("Basic ","")).split(":")
            username = auth_info[0]
            password = auth_info[1]
            return OpenmrsSession.authenticate(username,password)
        else : 
            print "no authorization header"
            return False
    
        

def angular_login(request):
    error = ajax_auth(request)
    r = json.dumps({"response":error});
    return HttpResponse(r,content_type='application/json')


def ajax_patient_search(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    search_string = get_var_from_request(request,"search_string")
    patients = ''
    if len(search_string) > 3 :
        patients = Patient.search_patients(search_string)
    data = json.dumps(patients)
    return HttpResponse(data,content_type='application/json')


@login_required    
def index(request):    
    print 'rendering outreach webapp'
    if Authorize.authorize(request.user,['superuser','outreach_manager','outreach_all']) :
        return render(request,'outreach_webapp/index_superuser.html',{})
    else : return render(request,'outreach_webapp/index.html',{})



def ajax_get_defaulter_cohort(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    '''
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    '''

    defaulter_cohort_id = get_var_from_request(request,'defaulter_cohort_id')    
    defaulter_cohort_uuid = get_var_from_request(request,'defaulter_cohort_uuid')
    
    print 'getting defaulter list'
    d = ''
    if(defaulter_cohort_id) : d = CohortCache.get_cohort(defaulter_cohort_id)
    elif(defaulter_cohort_uuid) : d = CohortCache.get_cohort(cohort_uuid=defaulter_cohort_uuid)
        
    return HttpResponse(d,content_type='application/json')


def ajax_get_new_defaulter_cohort(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    defaulter_cohort_id = get_var_from_request(request,'defaulter_cohort_id')    
    defaulter_cohort_uuid = get_var_from_request(request,'defaulter_cohort_uuid')
    
    if defaulter_cohort_id : dc = DefaulterCohort.objects.get(id=defaulter_cohort_id)
    else : dc = DefaulterCohort.objects.get(uuid=defaulter_cohort_uuid)
    
    new_dc = DefaulterCohort.create_defaulter_cohort(old_defaulter_cohort_id=dc.id)    
    d = CohortCache.get_cohort(dc.id)

    return HttpResponse(d,content_type='application/json')
    

def ajax_update_defaulter_cohort(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    cohort_id = get_var_from_request(request,"defaulter_cohort_id")
    patient_uuids = list(DefaulterCohortMember.objects.filter(defaulter_cohort_id=cohort_id,retired=1).values_list("patient_uuid",flat=True))
    if len(patient_uuids) > 0 : d = json.dumps(patient_uuids)
    else : d = json.dumps([])
    return HttpResponse(d,content_type='application/json')

def ajax_get_retired_members(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    cohort_uuid = get_var_from_request(request,"defaulter_cohort_uuid")
    dc = DefaulterCohort.objects.get(uuid=cohort_uuid);

    if dc.retired : d = json.dumps(["*"])
    else :
        patient_uuids = list(DefaulterCohortMember.objects.filter(uuid=cohort_uuid,retired=1).values_list("patient_uuid",flat=True))
        if len(patient_uuids) > 0 : d = json.dumps(patient_uuids)
        else : d = json.dumps([])
    

    return HttpResponse(d,content_type='application/json')
    
    

def ajax_submit_encounter(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    log = EncounterForm.process_encounter(request.POST,request.user.id)           
    key = request.POST.get("key","")
    data = json.dumps({"key":key})

    defaulter_cohort_id = get_var_from_request(request,'defaulter_cohort_id')    
    if defaulter_cohort_id:        
        try :
            import datetime
            patient_uuid = get_var_from_request(request,'patient_uuid')
            enc_date = datetime.datetime.strptime(get_var_from_request(request,"encounter_datetime"),"%Y-%m-%d")
            print "encounter date: " + str(enc_date)            
            member = DefaulterCohortMember.objects.filter(defaulter_cohort_id=defaulter_cohort_id,patient_uuid=patient_uuid)[0]
            member.update_status({"next_appt_date":enc_date,"next_encounter_type":"21"})        
        except Exception, e:
            print "ajax_submit_encounter(): error updating member : " + str(e)
            
    return HttpResponse(data,content_type='application/json')




def ajax_update_phone_number(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    phone_number = request.POST['phone_number']
    patient_uuid = request.POST['patient_uuid']
    attr_type_uuid = '72a759a8-1359-11df-a1f1-0026b9348838'
    log = PersonAttribute.create_person_attribute_rest(person_uuid=patient_uuid,person_attribute_type_uuid=attr_type_uuid,value=phone_number)    
    result = json.dumps(log.error)
    return HttpResponse(result,content_type='application/json')





def ajax_get_patient(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    patient_uuid = request.GET.get('patient_uuid',None)
    print "User : " + str(request.user.id) + " : requesting information on patient : " + patient_uuid
    p = Patient.get_patient_by_uuid(patient_uuid)
    data = json.dumps(p)
    return HttpResponse(data,content_type='application/json')


def ajax_get_outreach_providers(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    providers = Provider.get_outreach_providers()
    data = json.dumps(providers)
    return HttpResponse(data,content_type="application/json")


def ajax_is_defaulter_cohort_retired(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    id = get_var_from_request(request,'defaulter_cohort_id')
    dc = DefaulterCohort.objects.get(id=id)
    data = "false"
    if dc.retired : data = "true"
    return HttpResponse(data,content_type="application/json")



def ajax_get_locations(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    locations = Location.get_locations()
    data = json.dumps(locations)
    return HttpResponse(data,content_type="application/json")


def ajax_get_defaulter_cohorts(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    dcs = DefaulterCohort.objects.filter(retired=0).order_by("name")
    cohorts = []
    for dc in dcs :
        cohorts.append({"id":dc.id,"name":dc.name.title(),"uuid":dc.uuid})
    data = json.dumps(cohorts)
    return HttpResponse(data,content_type="application/json")


def test(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    return render(request,"outreach_webapp/angular_index.html",{})



# This function will save all non-retired cohorts as json strings to the db each morning.
# It will then serve these jsons to the web client (rather than querying the amrs database each time)
def ajax_update_cohort_cache(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    try:
        CohortCache.update_cohorts()
    except Exception, e:
        print e

    return HttpResponse("",content_type="application/json")



def ajax_get_encounter_data(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    patient_uuid = get_var_from_request(request,"patient_uuid")
    print "ajax_get_encounter_data() : getting data for patient uuid = " + str(patient_uuid)
    encounter_data = Patient.get_encounter_data(patient_uuid)
    data = json.dumps(encounter_data)
    return HttpResponse(data,content_type="application/json")



def ajax_get_encounter_full(request):
    if not ajax_auth(request):
        return HttpResponseForbidden()

    encounter_uuid = get_var_from_request(request,"encounter_uuid")
    print "ajax_get_encounter() : getting data for encounter uuid = " + str(encounter_uuid)
    encounter = Encounter.get_encounter(encounter_uuid)
    data = json.dumps(encounter)
    return HttpResponse(data,content_type="application/json")


@login_required
def update_datasets(request):
    import subprocess
    subprocess.call(["/home/amrs_reporting/amrs_reporting/database_updates/update_amrs_reporting_data"],shell=True)
    return HttpResponse("",content_type="application/json")
    
