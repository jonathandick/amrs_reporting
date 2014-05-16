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
from xlrd import open_workbook
from xlwt import Workbook, easyxf,Formula
from xlutils.copy import copy
import pytz
from datetime import datetime, date

# Create your views here.


@login_required
def index(request):
    if not Authorize.authorize(request.user) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    locations = Location.get_locations()
    location_groups = DerivedGroup.objects.filter(base_class='Location').order_by('name')

    #rt = ReportTable.objects.filter(name='retention_key_indicators')[0]    
    #key_indicators = rt.run_report_table(as_dict=True)['rows']
    key_indicators = {}
    providers = Provider().get_outreach_providers()

    ltfu_by_clinic = request.session.get('ltfu_by_clinic')
    ltfu_periods = request.session.get('ltfu_periods')
    if ltfu_by_clinic is None :
        ltfu_date = date(2014,1,1)
        cur_date = date.today()    
        rt = ReportTable.objects.filter(name='ltfu_by_clinic')[0]
        ltfu_by_clinic = {}
        ltfu_periods = []
        final_period = ''
        prev_ltfu = {}
        while ltfu_date <= cur_date :
            parameter_values = (str(ltfu_date),)
            rows = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']
            for row in rows :
                if row['name'] in ltfu_by_clinic : 
                    ltfu_by_clinic[row['name']][str(ltfu_date)]=row['num_ltfu'] 
                    ltfu_by_clinic[row['name']][str(ltfu_date) + '_diff'] = row['num_ltfu'] - prev_ltfu[row['name']]

                    # this will be rewritten each time so that the last iteration is the final period
                    ltfu_by_clinic[row['name']]['final_period'] = str(ltfu_date)
                else : 
                    ltfu_by_clinic[row['name']] = {str(ltfu_date):row['num_ltfu']}
                    ltfu_by_clinic[row['name']]['initial_period']=str(ltfu_date)
                prev_ltfu[row['name']] = row['num_ltfu']

            ltfu_periods.append(str(ltfu_date))
            if ltfu_date.month == 12 : ltfu_date = date(ltfu_date.year+1,1,1)
            else : ltfu_date = date(ltfu_date.year,ltfu_date.month+1,1)
                    

        request.session['ltfu_by_clinic'] = ltfu_by_clinic
        request.session['ltfu_periods'] = ltfu_periods

    return render(request,'ltfu/index.html',
                  {'locations':locations,
                   'location_groups':location_groups,
                   'key_indicators':key_indicators,
                   'providers':providers,
                   'ltfu_by_clinic':ltfu_by_clinic,
                   'ltfu_periods':ltfu_periods,
                   })


@login_required
def ltfu_ampath(request):
    if not Authorize.authorize(request.user,['outreach_all']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    rt = ReportTable.objects.filter(name='ltfu_ampath')[0]
    result = rt.run_report_table(as_dict=True)
    rows = result['rows']
    totals = {}
    for row in rows :
        for key, value in row.items():
            try :
                totals[key] = int(totals[key]) + int(value)
            except Exception, e :
                print str(e) + ' in exception'

    return render(request,"ltfu/ltfu_ampath.html",
                  {'report_table':rt,
                   'ltfu_ampath_table':rows,
                   'totals':totals,
                   })


@login_required
def ltfu_clinics(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    rt = ReportTable.objects.filter(name='ltfu_clinics')[0]
    ltfu_clinics_table = rt.run_report_table(as_dict=True)['rows']
    parameters = ReportTableParameter.objects.filter(report_table_id=rt.id)
    return render(request,"ltfu/ltfu_clinics.html",
                  {'report_table':rt,
                   'ltfu_clinics_table':ltfu_clinics_table,
                   'parameters':parameters,
                   })

    
                  
@login_required
def ltfu_clinic(request):
    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    location_id = get_var_from_request(request,'location_id')
    locations = Location().get_locations()
    location = Location().get_location(location_id)

    ltfu_date = get_var_from_request(request,'ltfu_date')

    if location_id :
        rt = ReportTable.objects.filter(name='ltfu_clinic')[0]
        parameter_values = (ltfu_date,location_id)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']

        rt = ReportTable.objects.filter(name='ltfu_stats')[0]
        result = rt.run_report_table(as_dict=True)
        ltfu_stats = result['rows']
        return render(request,'ltfu/ltfu_clinic.html',
                      {'ltfu_clinic_table':table,
                       'locations':locations,
                       'location':location,
                       'ltfu_stats':ltfu_stats,
                       }
                      )
    
                       
@login_required
def ltfu_by_range(request):
    location_id = get_var_from_request(request,'location_id')
    location_group_id = get_var_from_request(request,'location_group_id')
    g = None
    if location_group_id :
        g = DerivedGroup.objects.get(id=location_group_id)
        location_ids = tuple(g.get_member_ids())
    else : location_ids = (location_id,)

    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all'],list(location_ids)) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')


    start_range_high_risk = int(get_var_from_request(request,'start_range_high_risk'))
    if not start_range_high_risk : start_range_high_risk = 8
    start_range = int(get_var_from_request(request,'start_range'))
    if not start_range : start_range = 30
    end_range = int(get_var_from_request(request,'end_range'))
    if not end_range : end_range = 89

    limit = get_var_from_request(request,'limit')
    locations = Location.get_locations()
    location = Location.get_location(location_id)
    location_groups = DerivedGroup.objects.filter(base_class='Location').order_by('name')

    risk_categories = {0:'Being Traced',1:'high',2:'medium',3:'low',4:'LTFU',5:'no_rtc_date',6:'untraceable'}    

    if location_ids:
        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range_high_risk,start_range,end_range,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit)['rows']
        
        counts = {'tracing':0,'high':0,'medium':0,'low':0,'LTFU':0,'total':0,'no_rtc_date':0,'untraceable':0,'on_list_two_weeks':0}
        total = 0
        for row in table:
            if row['risk_category'] >= 0 :
                
                if row['risk_category'] == 0 : counts['tracing'] += 1
                else : counts[risk_categories[row['risk_category']]] +=1            
                counts['total'] +=1
                if row['risk_category'] == 1 and row['days_since_rtc'] >= 22 : counts['on_list_two_weeks'] += 1 
                elif row['days_since_rtc'] >= 44 : counts['on_list_two_weeks'] += 1 


        return render(request,'ltfu/ltfu_by_range.html',
                      {'ltfu_by_range':table,
                       'locations':locations,
                       'location_groups':location_groups,
                       'location':location,
                       'location_group':g,                       
                       'start_range':start_range,
                       'end_range':end_range,
                       'start_range_high_risk':start_range_high_risk,
                       'limit':limit,
                       'counts':counts,
                       }
                      )
    else :
        return HttpResponseRedirect('/ltfu/index')    


                       


@login_required
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


@login_required
def ltfu_get_defaulter_list(request):
    location_id = get_var_from_request(request,'location_id')
    location_group_id = get_var_from_request(request,'location_group_id')
    g = None
    if location_group_id :
        g = DerivedGroup.objects.get(id=location_group_id)
        location_ids = tuple(g.get_member_ids())
    else : location_ids = (location_id,)

    if not Authorize.authorize(request.user,['outreach_supervisor','outreach_all'],list(location_ids)) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    start_range_high_risk = int(get_var_from_request(request,'start_range_high_risk'))
    if not start_range_high_risk : start_range_high_risk = 8
    start_range = int(get_var_from_request(request,'start_range'))
    if not start_range : start_range = 30
    end_range = int(get_var_from_request(request,'end_range'))
    if not end_range : end_range = 89

    limit = get_var_from_request(request,'limit')
    locations = Location.get_locations()
    location = Location.get_location(location_id)
    location_groups = DerivedGroup.objects.filter(base_class='Location').order_by('name')


    if location_id or location_group_id:

        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range_high_risk,start_range,end_range,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit)['rows']
        if location_id : location_name = location['name']
        else : location_name = g.name
        
        date = datetime.today()        
        template_dir = '/home/amrs_reporting/amrs_reporting/amrs_reporting/ltfu/'
        template_file = 'outreach_registers.xls'
        new_file = location_name + '_defaulters_list_' + date.strftime('%Y_%m_%d') + '.xls'

        template = open_workbook(template_dir + template_file,formatting_info=True)
        
        book = copy(template)
        sheet = book.get_sheet(2)

        cur_row = 2
        risk_categories = {'0':'Being Traced','1':'high','2':'medium','3':'low','4':'LTFU','5':'no rtc date','6':'untraceable'}

        row_style = easyxf('font : height 400;')        
        cell_style = easyxf('borders: left thin, right thin, top thin, bottom thin;'
                            'alignment: wrap 1;')
        
        sheet.row(0).set_style(row_style)
        sheet.write(0,0,'General Defaulters List v1.0 : ' + location_name,easyxf('font : height 350, bold true;' 
                                                                            'borders: left thin, right thin, top thin, bottom thin;'))
        sheet.write(0,7,date.strftime('DATE CREATED:\n%d/%m/%Y'),
                    easyxf('font : height 175, bold true;'
                           'alignment: horizontal left, wrap 1;'
                           'borders: left thin, right thin, top thin, bottom thin;'))

        for row in table :
            sheet.row(cur_row).set_style(row_style)
            sheet.write(cur_row,0,cur_row-1,cell_style)
    
            s = str(get_val_from_row(row,'encounter_datetime')) 
            s += ' (' + str(get_val_from_row(row,'name')) + ') /\n' 
            s += str(get_val_from_row(row,'rtc_date')) + ' (' 
            s += str(get_val_from_row(row,'days_since_rtc')) + ')'

            sheet.write(cur_row,1,s,cell_style)

            #sheet.write(cur_row,1,str(row['encounter_datetime']) + ' (' + row['name'] + ') /\n' + str(row['rtc_date']) + ' (' + str(row['days_from_rtc_date']) + ')'
            #            ,cell_style)
            sheet.write(cur_row,2,risk_categories[str(row['risk_category'])],cell_style)
            sheet.write(cur_row,3,row['person_name'],cell_style)
            sheet.write(cur_row,4,row['identifier'],cell_style)
            sheet.write(cur_row,5,row['phone_number'],cell_style)
            sheet.write(cur_row,6,'',cell_style)
            sheet.write(cur_row,7,'',cell_style)

            cur_row += 1

        response = HttpResponse(mimetype="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=%s' % new_file
            
        book.save(response)
        
        return response


def view_outreach_worker_forms_done(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    rt = ReportTable.objects.filter(name='outreach_worker_forms_done')[0]
    table = rt.run_report_table(as_dict=True)['rows']
     
    return render(request,'ltfu/forms_done.html',
                  {'forms_done' : table,
                   })



def view_indicators_by_clinic(request):
    if not Authorize.authorize(request.user,['outreach_all','outreach_manager']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    start_date = get_var_from_request(request,'start_date')
    if start_date is None : start_date = '2014-01-01'
    end_date = get_var_from_request(request,'end_date')
    if end_date is None : end_date = '2020-01-01'
    

    
    rt = ReportTable.objects.get(name='outreach_indicators_by_clinic')
    parameter_values = (start_date,end_date)
    table = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']
        
    return render(request,'ltfu/outreach_indicators.html',
                  {'indicators':table,
                   'start_date':start_date,
                   'end_date':end_date,
                   'query_subject':'clinic',
                   }
                  )
    

def view_indicators_by_provider(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    start_date = get_var_from_request(request,'start_date')
    if start_date is None : start_date = '2014-01-01'
    end_date = get_var_from_request(request,'end_date')
    if end_date is None : end_date = '2020-01-01'
    
    rt = ReportTable.objects.get(name='outreach_indicators_by_provider')
    parameter_values = (start_date,end_date)
    table = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']
        
    return render(request,'ltfu/outreach_indicators.html',
                  {'indicators':table,
                   'start_date':start_date,
                   'end_date':end_date,
                   'query_subject':'provider',
                   }
                  )
    


    
