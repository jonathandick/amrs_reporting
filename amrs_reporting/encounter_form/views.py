from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from encounter_form.models import *
from amrs_interface.models import *

# Create your views here.

@login_required
def view_rest_errors(request):    
    log_ids = RESTLog.objects.filter(result_uuid=None,retired=False).values_list("id",flat=True)
    logs = EncounterLog.objects.filter(rest_log_id__in=log_ids)    
    errors = []
    return render(request,'encounter_form/view_rest_errors.html',{'errors':logs})


@login_required
def ajax_resubmit_encounter(request):
    log_id = request.POST['log_id']
    print 'LOG ID: ' + str(log_id)
    log = EncounterLog.objects.get(id=log_id)
    result = log.resubmit()
    return HttpResponse(result,content_type='application/json')



@login_required
def resubmit_encounter(request):
    log_id = request.POST['log_id']
    print 'LOG ID: ' + str(log_id)
    log = EncounterLog.objects.get(id=log_id)
    result = log.resubmit()
    return view_rest_errors(request) 



@login_required
def delete_encounter_log(request):
    id = int(request.GET['id'])
    EncounterLog.objects.get(id=id).delete()
    return HttpResponseRedirect('/encounter_form/view_rest_errors')



@login_required
def edit_encounter(request):
    if request.method == "GET":
        log_id = get_var_from_request(request,'log_id')
        log = EncounterLog.objects.get(id=log_id)
        form_vals = log.get_form_vals()
        locations = Location.get_locations()
        providers = Provider.get_outreach_providers()
        patient = Patient.get_patient_by_uuid(log.patient_uuid)
        device = get_device(request)
        args = {'log':log,
                'patient':patient,
                'form_vals':form_vals,
                'providers':providers,
                'locations':locations,
                'device':device,
                }    
        return render(request,'encounter_form/edit_encounter_form.html',args)
    else:
        log_id = get_var_from_request(request,'encounter_log_id')
        log = EncounterForm.reprocess_encounter(log_id,request.POST)
        return HttpResponseRedirect('/encounter_form/view_rest_errors')
