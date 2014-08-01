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

    clinic_indicators = request.session.get('hiv_clinic_indicators')
    if clinic_indicators is not None : clinic_indicators = simplejson.loads(clinic_indicators)

    if system_indicators is None :
        try:
            rt = ReportTable.objects.get(name='hiv_system_key_indicators')
            system_indicators = rt.run_report_table(as_dict=True)['rows']

            #rt = ReportTable.objects.get(name='hiv_clinic_key_indicators')
            #clinic_indicators = rt.run_report_table(as_dict=True)['rows']
    
            if system_indicators : 
                print 'saving system indicators to session'
                request.session['system_indicators'] = simplejson.dumps(system_indicators)
            
                if clinic_indicators : 
                    print 'saving clinic indicators to session'
                    request.session['clinic_indicators'] = simplejson.dumps(clinic_indicators)
        except Exception, e:
            pass


    return render(request,'hiv_dashboard/index.html',
                  {'locations':locations,
                   'location_groups':location_groups,
                   'system_indicators':system_indicators,
                   'clinic_indicators':clinic_indicators,
                   })

