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



def toHTML(concept_uuid,data_type):
    concept = Concept.get_concept_info(concept_uuid)
    s = ''    
    id = concept['name'].lower().replace(' ','_')

    if data_type == 'select':
        s = "<label for='" + id + "'>" + concept['name'].capitalize() + "</label>\n"
        s += "<select id='" + id + "' name='obs__" + concept_uuid + "'>\n"
        for a in concept['answers'] :
            s += "\t<option value='" + a['uuid'] + "'>" + a['name'].capitalize() + "</option>\n"
        s += "</select>"
    
    if data_type == 'text':
        s = "<label for='" + id + "'>" + concept['name'].capitalize() + "</label>\n"
        s += "<input id='" + id + "' name='obs__" + concept_uuid + "' type='text'/>"

    if data_type == "checkbox":
        s = "<legend>" + concept['name'].title() + "</legend>\n"
        for a in concept['answers'] :
            key = id + "." + a['name'].lower().replace(' ','_')
            s += "<input name='" + a['uuid'] + "' id='" + key + "' type='checkbox' value='" + a['uuid'] + "'/>\n"
            s += "<label for='" + key + "'>" + a['name'].capitalize() + "</label>\n"        

    return s



@login_required
def build_schema(request):
    if request.method == "GET":
        return render(request,'encounter_form/build_schema.html',{})
    else :        
        args = request.POST
        s = ''
        for k,v in args.iteritems() :
            parts = k.split('__')
            if len(parts) > 0 and parts[0] == 'input':
                concept_uuid = parts[1]
                data_type = str(v)
                html = toHTML(concept_uuid,data_type)
                s += html + "\n\n"
            
        data = json.dumps(s)
        return HttpResponse(data,content_type='application/json')


@login_required
def ajax_concept_search(request):
    search_string = request.POST['search_string']
    concepts = ''
    if len(search_string) >= 3 :
        concepts = Concept.search_concepts(search_string)
    data = json.dumps(concepts)
    print 'returning ajax concept search'
    return HttpResponse(data,content_type='application/json')



@login_required
def test(request):

    logs = RESTLog.objects.filter(result_uuid=None,retired=0)
    for l in logs:
        if "attribute" in l.url:
            RESTHandler.repost(log=l)
            print l.result_uuid
            
            

    
    
