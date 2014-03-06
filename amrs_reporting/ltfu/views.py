from report.models import *
from utilities import *
from ltfu.models import *
# Create your views here.


def index(request):
    locations = Location().get_locations()    
    rt = ReportTable.objects.filter(name='ltfu_stats')[0]
    result = rt.run_report_table(as_dict=True)
    ltfu_stats = result['rows']
    parameters = ReportTableParameter.objects.filter(report_table_id=rt.id)
    return render(request,'ltfu/index.html',
                  {'locations':locations,
                   'ltfu_stats':ltfu_stats,
                   'ltfu_stats_parameters':parameters,
                   })


def ltfu_ampath(request):
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


def ltfu_clinics(request):
    rt = ReportTable.objects.filter(name='ltfu_clinics')[0]
    ltfu_clinics_table = rt.run_report_table(as_dict=True)['rows']
    parameters = ReportTableParameter.objects.filter(report_table_id=rt.id)
    return render(request,"ltfu/ltfu_clinics.html",
                  {'report_table':rt,
                   'ltfu_clinics_table':ltfu_clinics_table,
                   'parameters':parameters,
                   })

    
                  
def ltfu_clinic(request):
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
    
                       
def ltfu_by_range(request):
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
    

                       


def run_report_table(request):
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

