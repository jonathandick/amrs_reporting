from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
import pytz
import simplejson
from django.contrib.sessions.models import Session
from report.models import Report, ReportTable, ReportTableParameter, ReportMember
from amrs_user_validation.models import Authorize
import utilities



# Create your views here.

def view_datasets(request):
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    if request.method == 'POST' :
        pass
    else :
        pass


def create_dataset(request):
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    if request.method == 'POST' :
        pass

    else :
        dataset_id = get_var_from_request(request,'dataset_id')
        d = None
        if dataset_id is not None :
            d = AmrsDataset.objects.filter(id=dataset_id)
        return render(request,'amrs_data_manager/create_dataset.html',{'dataset':d})
    






