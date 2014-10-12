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



@login_required    
def index(request):    
    cohorts = DefaulterCohort.objects.filter(retired=0).order_by('name')
    locations = Location.get_locations()
    print "getting providers..."
    providers = Provider.get_outreach_providers()
    print 'rendering outreach webapp'
    return render(request,'outreach_webapp/index.html',{'defaulter_cohorts':cohorts,
                                                        'locations':locations,
                                                        'providers':providers})

@login_required
def ajax_get_defaulter_cohort(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    defaulter_cohort_id = request.POST['defaulter_cohort_id']

    dc = DefaulterCohort.objects.get(id=defaulter_cohort_id)

    data = request.session.get(dc.location_uuid,'')
    if data is not None and data != '':
        patients = json.loads(request.session.get(dc.location_uuid,''))
    else :
        patients = dc.get_patients()
        request.session[dc.location_uuid] = json.dumps(patients, cls=DjangoJSONEncoder)

    d = {"name":dc.name,"date_created":dc.date_created,"patients":patients,"id":dc.id,"location_uuid":dc.location_uuid}
    d = json.dumps(d,cls=DjangoJSONEncoder)

    return HttpResponse(d,content_type='application/json')


@login_required
def ajax_update_defaulter_cohort(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    id = request.POST['defaulter_cohort_id']    
    print "removing dc with id: " + str(id)

    dc = DefaulterCohort.create_defaulter_cohort(old_defaulter_cohort_id=id)
    
    patients = dc.get_patients()
    request.session[dc.location_uuid] = json.dumps(patients, cls=DjangoJSONEncoder)

    d = {"name":dc.name,"date_created":dc.date_created,"patients":patients,"id":dc.id,"location_uuid":dc.location_uuid}
    d = json.dumps(d,cls=DjangoJSONEncoder)

    return HttpResponse(d,content_type='application/json')




@login_required
def ajax_submit_encounter(request):
    log = EncounterForm.process_encounter(request.POST,request.user.id)           
    print "ajax_submit_encounter() : " + str(log)

    key = request.POST.get("key","")
    data = json.dumps({"key":key})

    defaulter_cohort_id = get_var_from_request(request,'defaulter_cohort_id')    
    if defaulter_cohort_id:        
        try :
            import datetime
            patient_uuid = get_var_from_request(request,'patient_uuid')
            enc_date = datetime.strptime(get_var_from_request(request,"encounter_datetime"),"%Y-%m-%d")
            member = DefaulterCohortMember.objects.filter(defaulter_cohort_id=defaulter_cohort_id,patient_uuid=patient_uuid)[0]
            member.update_status({"next_appt_date":enc_date,"next_encounter_type":"OUTREACHFIELDFUP"})        
        except Exception, e:
            print "ajax_submit_encounter(): error updating member : " + e
            
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
    p = Patient.get_patient_by_uuid(patient_uuid)
    data = json.dumps(p)
    return HttpResponse(data,content_type='application/json')


@login_required
def ajax_get_outreach_providers(request):
    providers = Provider.get_outreach_providers()
    data = json.dumps(providers)
    return HttpResponse(data,content_type="application/json")


@login_required
def ajax_get_locations(request):
    locations = Location.get_locations()
    data = json.dumps(locations)
    return HttpResponse(data,content_type="application/json")


@login_required
def ajax_get_defaulter_cohorts(request):
    dcs = DefaulterCohort.objects.filter(retired=0)
    cohorts = []
    for dc in dcs :
        cohorts.append({"id":dc.id,"name":dc.name})
    data = json.dumps(cohorts)
    return HttpResponse(data,content_type="application/json")



