from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
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


@login_required    
def index(request):    
    print 'rendering outreach webapp'
    if Authorize.authorize(request.user,['superuser','outreach_manager','outreach_all']) :
        return render(request,'outreach_webapp/index_superuser.html',{})
    else : return render(request,'outreach_webapp/index.html',{})


@login_required
def ajax_get_defaulter_cohort(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    defaulter_cohort_id = request.POST['defaulter_cohort_id']
    print 'getting defaulter list'
    d = CohortCache.get_cohort(defaulter_cohort_id)
    return HttpResponse(d,content_type='application/json')


@login_required
def ajax_get_new_defaulter_cohort(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    id = request.POST['defaulter_cohort_id']    
    
    dc = DefaulterCohort.create_defaulter_cohort(old_defaulter_cohort_id=id)    
    d = CohortCache.get_cohort(id)

    return HttpResponse(d,content_type='application/json')


@login_required
def ajax_update_defaulter_cohort(request):
    cohort_id = get_var_from_request(request,"defaulter_cohort_id")
    patient_uuids = list(DefaulterCohortMember.objects.filter(defaulter_cohort_id=cohort_id,retired=1).values_list("patient_uuid",flat=True))
    if len(patient_uuids) > 0 : d = json.dumps(patient_uuids)
    else : d = json.dumps([])
    return HttpResponse(d,content_type='application/json')
    
    

@login_required
def ajax_submit_encounter(request):
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




@login_required
def ajax_update_phone_number(request):
    phone_number = request.POST['phone_number']
    patient_uuid = request.POST['patient_uuid']
    attr_type_uuid = '72a759a8-1359-11df-a1f1-0026b9348838'
    log = PersonAttribute.create_person_attribute_rest(person_uuid=patient_uuid,person_attribute_type_uuid=attr_type_uuid,value=phone_number)    
    result = json.dumps(log.error)
    return HttpResponse(result,content_type='application/json')


@login_required
def ajax_patient_search(request):
    search_string = get_var_from_request(request,"search_string")
    patients = ''
    if len(search_string) > 3 :
        patients = Patient.search_patients(search_string)
    data = json.dumps(patients)
    return HttpResponse(data,content_type='application/json')



@login_required
def ajax_get_patient(request):
    patient_uuid = request.GET.get('patient_uuid',None)
    print "User : " + str(request.user.id) + " : requesting information on patient : " + patient_uuid
    p = Patient.get_patient_by_uuid(patient_uuid)
    data = json.dumps(p)
    return HttpResponse(data,content_type='application/json')


@login_required
def ajax_get_outreach_providers(request):
    providers = Provider.get_outreach_providers()
    data = json.dumps(providers)
    return HttpResponse(data,content_type="application/json")


@login_required
def ajax_is_defaulter_cohort_retired(request):
    id = get_var_from_request(request,'defaulter_cohort_id')
    dc = DefaulterCohort.objects.get(id=id)
    data = "false"
    if dc.retired : data = "true"
    return HttpResponse(data,content_type="application/json")



@login_required
def ajax_get_locations(request):
    locations = Location.get_locations()
    data = json.dumps(locations)
    return HttpResponse(data,content_type="application/json")


@login_required
def ajax_get_defaulter_cohorts(request):
    dcs = DefaulterCohort.objects.filter(retired=0).order_by("name")
    cohorts = []
    for dc in dcs :
        cohorts.append({"id":dc.id,"name":dc.name.title()})
    data = json.dumps(cohorts)
    return HttpResponse(data,content_type="application/json")


@login_required
def test(request):
    return render(request,"outreach_webapp/test.html",{})



# This function will save all non-retired cohorts as json strings to the db each morning.
# It will then serve these jsons to the web client (rather than querying the amrs database each time)
@login_required
def ajax_update_cohort_cache(request):
    try:
        CohortCache.update_cohorts()
    except Exception, e:
        print e

    return HttpResponse("",content_type="application/json")


@login_required
def ajax_get_encounter_data(request):
    patient_uuid = get_var_from_request(request,"patient_uuid")
    print "ajax_get_encounter_data() : getting data for patient uuid = " + str(patient_uuid)
    encounter_data = Patient.get_encounter_data(patient_uuid)
    data = json.dumps(encounter_data)
    return HttpResponse(data,content_type="application/json")


@login_required
def ajax_get_encounter_full(request):
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
    

