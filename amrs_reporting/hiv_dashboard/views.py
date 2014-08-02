from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from report.models import *
from utilities import *
from amrs_interface.models import *
from amrs_user_validation.models import Authorize
import pytz
from datetime import datetime, date
import simplejson


# Create your views here.


@login_required
def index(request):
    if not Authorize.authorize(request.user) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    locations = Location.get_locations()
    location_groups = DerivedGroup.objects.filter(base_class='Location').order_by('name')

    system_indicators = request.session.get('hiv_system_indicators')
    if system_indicators is not None : system_indicators = simplejson.loads(system_indicators)

    if system_indicators is None :
        try:
            rt = ReportTable.objects.get(name='hiv_system_key_indicators')
            system_indicators = rt.run_report_table(as_dict=True)['rows']

            if system_indicators : 
                print 'saving system indicators to session'
                request.session['system_indicators'] = simplejson.dumps(system_indicators)

        except Exception, e:
            pass


    return render(request,'hiv_dashboard/index.html',
                  {'locations':locations,
                   'location_groups':location_groups,
                   'system_indicators':system_indicators,
                   })


@login_required
def view_indicators_by_clinic(request):
    if not Authorize.authorize(request.user) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    locations = Location.get_locations()
    location_groups = DerivedGroup.objects.filter(base_class='Location').order_by('name')
    start_date = get_var_from_request(request,'start_date')
    if start_date is None : start_date = '2000-01-01'

    end_date = get_var_from_request(request,'end_date')
    if end_date is None : end_date = '2020-01-01'
    try:
        values = (start_date,end_date,)
        rt = ReportTable.objects.get(name='hiv_clinic_key_indicators')
        clinic_indicators = rt.run_report_table(parameter_values=values,as_dict=True)['rows']

    except Exception, e:
        clinic_indicators = {}
        print e

    return render(request,'hiv_dashboard/key_indicators_by_clinic.html',
                  {'locations':locations,
                   'location_groups':location_groups,
                   'clinic_indicators':clinic_indicators,
                   'start_date':start_date,
                   'end_date':end_date,
                   })


@login_required
def view_indicators_by_month(request):
    if not Authorize.authorize(request.user) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    locations = Location.get_locations()
    location_groups = DerivedGroup.objects.filter(base_class='Location').order_by('name')

    start_date = get_var_from_request(request,'start_date')
    if start_date is None : start_date = '2000-01-01'

    end_date = get_var_from_request(request,'end_date')
    if end_date is None : end_date = '2020-01-01'

    location_id = get_var_from_request(request,'location_id')
    location = Location.get_location(location_id)

    values = (start_date,end_date,location_id,)

    try:
        rt = ReportTable.objects.get(name='hiv_key_indicators_by_month')
        clinic_indicators = rt.run_report_table(as_dict=True,parameter_values=values)['rows']
        
    except Exception, e:
        pass


    return render(request,'hiv_dashboard/key_indicators_by_month.html',
                  {'locations':locations,
                   'location_groups':location_groups,
                   'clinic_indicators':clinic_indicators,
                   'location':location,
                   'start_date':start_date,
                   'end_date':end_date,
                   })

