from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from pytz import timezone
import pytz
import simplejson
from django.contrib.sessions.models import Session
from report.models import Report, ReportTable, ReportTableParameter, ReportMember
import ast
# from weasyprint import HTML, default_url_fetcher, CSS
from amrs_user_validation.models import Authorize
from ltfu.models import DefaulterCohort
import utilities as u
# Admin *********************************************************************************

@login_required
def index(request):
    if not Authorize.authorize(request.user) :
        return HttpResponseRedirect('amrs_user_validation/access_denied')
    device = u.get_device(request)

    if device['is_mobile']: return render(request, "amrs_reports/index_mobile.html",{})
    else : return render(request, "amrs_reports/index_mobile.html",{})
                         



@login_required
def manage_report_tables(request):
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    report_tables = ReportTable.objects.all()
    return render(request, "amrs_reports/manage_report_tables.html",
                  {'report_tables':report_tables,
                   })

@login_required
def manage_reports(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    reports = Report.objects.all()
    return render(request, "amrs_reports/manage_reports.html",
                  {'reports':reports,
                   })

# ReportTable Views *************************************************************************

def create_report_table(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    if request.method == "POST" :
        name = get_var(request.POST,'name')
        report_table_sql = get_var(request.POST,'report_table_sql')
        description = get_var(request.POST,'description')
        report_table_id = get_var(request.POST,'report_table_id')        
        if name and report_table_sql:
            if report_table_id : 
                rt = ReportTable.objects.get(id=report_table_id)
                rt.name = name
                rt.description = description
                rt.report_table_sql = report_table_sql
                ReportTableParameter.objects.filter(report_table_id=rt.id).delete()
            else :
                rt = ReportTable(name=name,report_table_sql=report_table_sql,description=description)            
            rt.save()
            count = report_table_sql.count('%s')
            rt.create_parameters(request.POST,count)
                                                    
        return HttpResponseRedirect('/amrs_reports/manage_report_tables')
    else :
        report_table_id = get_var(request.GET,'report_table_id')
        rt = None
        parameters = []
        if report_table_id :
            rt = ReportTable.objects.get(id=report_table_id)            
            parameters = rt.get_parameters()
        return render(request, "amrs_reports/create_report_table.html",
                      {'report_table':rt,
                       'parameters': parameters,
                       })


def delete_report_table(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    if 'report_table_id' in request.GET:
        rt = ReportTable.objects.get(id=request.GET['report_table_id'])
        rt.delete()
    return HttpResponseRedirect('/')


def run_report_table(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')


    report_table_id = get_var_from_request(request,'report_table_id')
    if report_table_id :
        rt = ReportTable.objects.get(id=report_table_id)
        result = rt.run_report_table(request.POST)
        cols = result['cols']
        rows = result['rows']
        parameters = ReportTableParameter.objects.filter(report_table_id=rt.id)
        return render(request,"amrs_reports/view_report_table.html",
                      {'report_table':rt,
                       'cols':cols,
                       'rows':rows,
                       'parameters':parameters,                       
                       })


    else :
        report_tables = ReportTable.objects.all()
        return render(request, "amrs_reports/run_report_table.html",
                      {'report_tables':report_tables,
                       })

            

# Report Views *******************************************************************************
def create_report(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    if request.method == "POST" :
        print request.POST
        name = get_var(request.POST,'report_name')
        description = get_var(request.POST,'description')
        template = get_var(request.POST,'template')
        report_id = get_var(request.POST,'report_id')
        if name :
            if report_id : 
                r = Report.objects.get(id=report_id)
                r.name = name
                r.description = description
            else :
                r = Report(name=name,description=description)                        
            r.save()
            cur_index = 2            
            while True :                
                row = get_var(request.POST,'report_table_values_' + str(cur_index))
                if row is None : break 
                rm = ReportMember(report_id=r.id)
                args = row.split(';;;')

                for arg in args :
                    split = arg.split('===')
                    setattr(rm,split[0],split[1])
                rm.save()            
                cur_index += 1

                     
        return HttpResponseRedirect('/')
    else :        
        report_id = get_var(request.GET,'report_id')
        report_tables = ReportTable.objects.all().order_by('name')
        r = None
        if report_id :
            r = Report.objects.get(id=report_id)            
        return render(request, "amrs_reports/create_report.html",
                      {'report':r,
                       'report_tables':report_tables,
                       })
            

def delete_report(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    if 'report_id' in request.GET:
        r = Report.objects.get(id=request.GET['report_id'])
        ReportMember.objects.filter(report_id=r.id).delete()
        r.delete()

    return HttpResponseRedirect('/')


def run_report(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    report_id = get_var_from_request(request,'report_id')
    if report_id :        
        r = Report.objects.get(id=report_id)
        args = r.run_report(request.POST)
        template = r.template
        if template is None or template == '' :
            template = "amrs_reports/view_report.html"

        return render(request,template,
                      {'report':r,
                       'report_members':args,  
                       })


    else :
        report_tables = ReportTable.objects.all()
        return render(request, "amrs_reports/run_report.html",
                      {'report_tables':report_tables,
                       })

    if request.method == "POST":
        report_id = get_var(request.POST,'report_id')
        r = Report.objects.get(id=report_id)
        result = r.run_report(request.POST)
        return render(request,result[0],result[1])


def get_report_as_pdf(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    
    report_id = get_var_from_request(request,'report_id')
    if report_id :        
        r = Report.objects.get(id=report_id)
        args = r.run_report(request.POST)
        template = r.template
        if template is None or template == '' :
            template = "amrs_reports/view_report_pdf.html"
        template = get_template(template)
        context = {'report':r, 'report_members':args,}               
        html = template.render(RequestContext(request, context))
        
        response = HttpResponse(mimetype="application/pdf")
        HTML(string=html,url_fetcher=my_fetcher,base_url=request.build_absolute_uri()).write_pdf(response)
        return response
    


def get_system_time(request):
    if request.is_ajax():
        ret = []
        ret.append({'id':'#system_time',
                    'time': strftime("%a, %d %b %Y %H:%M %Z%z", localtime())})
        ret = simplejson.dumps(ret)
        return HttpResponse(ret,mimetype='application/javascript')
                           


def update_datasets(request):
    pass


# Utility Functions ********************************************************************************

def get_var(d,var_name):
    if var_name in d and d[var_name] != '' : return d[var_name]
    else : return None

def get_var_from_request(request,var_name):
    if var_name in request.POST and request.POST[var_name] != '' : return request.POST[var_name]
    elif var_name in request.GET and request.GET[var_name] != '' : return request.GET[var_name]
    else : return None


def my_fetcher(url):
    if url.startswith('/static/amrs_reports/images/'):                        
        with open(os.path.join('home/jdick/openmrs_env/reporting/amrs_reports',url)) as asset:
            contents = asset.read()
        return dict(string=contents)
    else:
        return default_url_fetcher(url)


