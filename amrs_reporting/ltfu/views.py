from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from report.models import *
from utilities import *
from ltfu.models import *
from amrs_user_validation.models import Authorize
from xlrd import open_workbook
from xlwt import Workbook, easyxf,Formula
from xlutils.copy import copy
import pytz
from datetime import datetime

# Create your views here.


@login_required
def index(request):
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    locations = Location().get_locations()    
    rt = ReportTable.objects.filter(name='ltfu_stats')[0]
    date = datetime.today()
    parameter_values = ('2014-01-01',date.strftime('%Y-%m-%d'))
    result = rt.run_report_table(parameter_values=parameter_values,as_dict=True)
    ltfu_stats = result['rows']
    parameters = ReportTableParameter.objects.filter(report_table_id=rt.id)
    return render(request,'ltfu/index.html',
                  {'locations':locations,
                   'ltfu_stats':ltfu_stats,
                   'ltfu_stats_parameters':parameters,
                   })


@login_required
def ltfu_ampath(request):
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    rt = ReportTable.objects.filter(name='ltfu_ampath')[0]
    result = rt.run_report_table(as_dict=True)
    rows = result['rows']
    totals = {}
    for row in rows :
        for key, value in row.items():
            try :
                print str(key) + ' : ' + str(value)
                totals[key] = int(totals[key]) + int(value)
            except Exception, e :
                print str(e) + ' in exception'
    print totals
    return render(request,"ltfu/ltfu_ampath.html",
                  {'report_table':rt,
                   'ltfu_ampath_table':rows,
                   'totals':totals,
                   })


@login_required
def ltfu_clinics(request):
    if not Authorize.authorize(request.user,['admin']) :        
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
    if not Authorize.authorize(request.user,['admin']) :        
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
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    location_id = get_var_from_request(request,'location_id')
    start_range = get_var_from_request(request,'start_range')
    end_range = get_var_from_request(request,'end_range')

    locations = Location().get_locations()
    location = Location().get_location(location_id)

    if location_id :
        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range,end_range,location_id)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']
        return render(request,'ltfu/ltfu_by_range.html',
                      {'ltfu_by_range':table,
                       'locations':locations,
                       'location':location,
                       }
                      )
    

                       


@login_required
def run_report_table(request):
    if not Authorize.authorize(request.user,['admin']) :        
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
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    location_id = get_var_from_request(request,'location_id')


    if location_id :
        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (30,90,location_id)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']
        
        location = Location().get_location(location_id)['name']
        date = datetime.today()        
        template_dir = '/home/jdick/dev/amrs_reporting/ltfu/'
        template_file = 'outreach_registers.xls'
        new_file = location + '_defaulters_list_' + date.strftime('%Y_%m_%d') + '.xls'

        template = open_workbook(template_dir + template_file,formatting_info=True)
        
        book = copy(template)
        sheet = book.get_sheet(2)

        cur_row = 2
        risk_categories = {'1':'high','2':'medium','3':'low'}


        row_style = easyxf('font : height 400;')        
        cell_style = easyxf('borders: left thin, right thin, top thin, bottom thin;'
                            'alignment: wrap 1;')
        
        sheet.row(0).set_style(row_style)
        sheet.write(0,0,'General Defaulters List v1.0 : ' + location,easyxf('font : height 350, bold true;' 
                                                                            'borders: left thin, right thin, top thin, bottom thin;'))
        sheet.write(0,7,date.strftime('DATE CREATED:\n%d/%m/%Y'),
                    easyxf('font : height 175, bold true;'
                           'alignment: horizontal left, wrap 1;'
                           'borders: left thin, right thin, top thin, bottom thin;'))

        for row in table :
            sheet.row(cur_row).set_style(row_style)
            sheet.write(cur_row,0,cur_row-1,cell_style)
            sheet.write(cur_row,1,str(row['encounter_datetime']) + ' (' + row['name'] + ') /\n' + str(row['rtc_date']) + ' (' + str(row['days_from_rtc_date']) + ')'
                        ,cell_style)
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
