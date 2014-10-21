from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.serializers.json import DjangoJSONEncoder
import pytz
from datetime import datetime, date

from report.models import *
from amrs_interface.models import *
from amrs_user_validation.models import Authorize
from defaulter_cohort.models import *
from encounter_form.models import *
import utilities as utilities



# Create your views here.
@login_required
def view_defaulter_cohort(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    location_uuid = request.GET['location_uuid']
    
    dc = DefaulterCohort.objects.filter(location_uuid=location_uuid,retired=0)[0]

    data = request.session.get(dc.location_uuid,'')
    if data is not None and data != '':
        patients = json.loads(request.session.get(dc.location_uuid,''))
    else :
        patients = dc.get_patients()        
        request.session[dc.location_uuid] = json.dumps(patients, cls=DjangoJSONEncoder)
        
    device = get_device(request)
    return render(request,'ltfu/view_defaulter_cohort_mobile.html',
                  {'defaulter_cohort':dc,
                   'patients':patients,
                   'device':device}
                  )

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



def update_defaulter_cohorts(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    print 'Updating cohorts .......................................'
    start = datetime.today()
    DefaulterCohort.update_defaulter_cohorts()
    t = datetime.today() - start
    print 'Time to update cohorts: ' + str(t.seconds)

    return HttpResponseRedirect('/ltfu/outreach_dashboard')


@login_required
def create_defaulter_cohort(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    location_uuid = request.GET['location_uuid']
    dc = DefaulterCohort.create_defaulter_cohort(location_uuid)
    patients = dc.get_patients()

    request.session[dc.location_uuid]=json.dumps(patients, cls=DjangoJSONEncoder)
    device = get_device(request)
    return render(request,'ltfu/view_defaulter_cohort_mobile.html',
                  {'defaulter_cohort':dc,
                   'patients':patients,
                   'device':device}
                  )
    

@login_required
def view_master_defaulter_list(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all','outreach_worker']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    location_uuid = request.GET['location_uuid']



@login_required
def manage_defaulter_cohorts(request):    
    if not Authorize.authorize(request.user,['superuser']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    dcs = DefaulterCohort.objects.all()    
    return render(request,
                  'ltfu/manage_defaulter_cohorts.html',
                  {"defaulter_cohorts":dcs,                   
                   }
                  )

@login_required
def delete_defaulter_cohort(request):
    if not Authorize.authorize(request.user,['superuser']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    cohort_uuid = request.GET['cohort_uuid']
    DefaulterCohort.delete_defaulter_cohort(cohort_uuid)
    return HttpResponseRedirect('/ltfu/manage_defaulter_cohorts')
