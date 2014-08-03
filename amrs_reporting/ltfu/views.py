from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template.loader import get_template
from django.template import Context, loader, RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from report.models import *
from utilities import *
from amrs_interface.models import *
from amrs_user_validation.models import Authorize
from xlrd import open_workbook
from xlwt import Workbook, easyxf,Formula
from xlutils.copy import copy
import pytz
from datetime import datetime, date
import simplejson
from ltfu.models import *
from django.core.serializers.json import DjangoJSONEncoder

# Create your views here.


@login_required
def index(request):
    if not Authorize.authorize(request.user) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    locations = Location.get_locations()
    location_groups = DerivedGroup.objects.filter(base_class='Location').order_by('name')

    key_indicators = {}
    providers = Provider().get_outreach_providers()

    defaulters_by_clinic = request.session.get('defaulters_by_clinic')
    if defaulters_by_clinic is not None : defaulters_by_clinic = simplejson.loads(defaulters_by_clinic)
    
    system_indicators = request.session.get('system_indicators')
    if system_indicators is not None : system_indicators = simplejson.loads(system_indicators)

    clinic_indicators = request.session.get('clinic_indicators')
    if clinic_indicators is not None : clinic_indicators = simplejson.loads(clinic_indicators)



    if defaulters_by_clinic is None :
        rt = ReportTable.objects.get(name='retention_key_indicators_system')
        system_indicators = rt.run_report_table(as_dict=True)['rows']

        rt = ReportTable.objects.get(name='retention_key_indicators_clinic')
        clinic_indicators = rt.run_report_table(as_dict=True)['rows']

        rt = ReportTable.objects.get(name='retention_defaulters_by_clinic') 
        defaulters_by_clinic = rt.run_report_table(as_dict=True)['rows']

                
        if system_indicators : 
            print 'saving system indicators to session'
            request.session['system_indicators'] = simplejson.dumps(system_indicators)

        if clinic_indicators : 
            print 'saving clinic indicators to session'
            request.session['clinic_indicators'] = simplejson.dumps(clinic_indicators)

        if defaulters_by_clinic : 
            print 'saving defaulters_by_clinic to session'
            request.session['defaulters_by_clinic'] = simplejson.dumps(defaulters_by_clinic)


    return render(request,'ltfu/index.html',
                  {'locations':locations,
                   'location_groups':location_groups,
                   'system_indicators':system_indicators,
                   'clinic_indicators':clinic_indicators,
                   'providers':providers,
                   'defaulters_by_clinic':defaulters_by_clinic,
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
        parameter_values = (start_range_high_risk,start_range,end_range,location_ids,location_ids)
        table = rt.run_report_table(parameter_values=parameter_values,as_dict=True,limit=limit)['rows']
        
        counts = {'tracing':0,'high':0,'medium':0,'low':0,'LTFU':0,'total':0,'no_rtc_date':0,'untraceable':0,'on_list_two_weeks':0}
        total = 0
        per_day = {}
        for row in table:
            if row['risk_category'] >= 0 :
                
                if row['risk_category'] == 0 : counts['tracing'] += 1
                else : counts[risk_categories[row['risk_category']]] +=1            
                counts['total'] +=1

                if row['days_since_rtc'] : days_since_rtc = int(row['days_since_rtc'])
                else : days_since_rtc = (date.today() - row['encounter_datetime']).days

                if (row['risk_category'] == 1 and days_since_rtc >= 22) or days_since_rtc >=44 : counts['on_list_two_weeks'] += 1 

                if days_since_rtc < 30 : days_since_rtc -= 8
                else : days_since_rtc -= 30
                if days_since_rtc in per_day : per_day[days_since_rtc] += 1
                else : per_day[days_since_rtc] = 1



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
                       'per_day':per_day,
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


    if location_ids:

        rt = ReportTable.objects.filter(name='ltfu_by_range')[0]
        parameter_values = (start_range_high_risk,start_range,end_range,location_ids,location_ids)
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


@login_required
def view_outreach_worker_forms_done(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    rt = ReportTable.objects.filter(name='outreach_worker_forms_done')[0]
    table = rt.run_report_table(as_dict=True)['rows']
     
    return render(request,'ltfu/forms_done.html',
                  {'forms_done' : table,
                   })

@login_required
def view_data_entry_forms_done(request):
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    rt = ReportTable.objects.filter(name='data_entry_forms_done')[0]
    table = rt.run_report_table(as_dict=True)['rows']
     
    return render(request,'ltfu/forms_done.html',
                  {'forms_done' : table,
                   })


@login_required
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
    
@login_required
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
    

@login_required
def view_reason_missed_appt(request):
    if not Authorize.authorize(request.user,['outreach_all']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    start_date = get_var_from_request(request,'start_date')
    if start_date is None : start_date = '2014-01-01'
    end_date = get_var_from_request(request,'end_date')
    if end_date is None : end_date = '2020-01-01'

    all_locations = 0
    location_ids_str = get_var_from_request(request,'location_ids')

    if location_ids_str is None or location_ids_str == '()':
        location_ids = ('-1',)
        all_locations = 1
        location_ids_str = ''
    else :
        location_ids = tuple(location_ids_str.split(','))


    rt = ReportTable.objects.get(name='retention_reason_missed_appt_total')
    parameter_values = (start_date,end_date,all_locations,location_ids)
    rows = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']
    times_asked = rows[0]['total']

    rt = ReportTable.objects.get(name='retention_reason_missed_appt')
    parameter_values = (start_date,end_date,all_locations,location_ids)
    rows = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']

    coded_reasons = {}
    concept_ids = []
    for row in rows :
        codes = row['reason_missed_appt'].split(' // ')
        for code in codes:
            if code in coded_reasons : coded_reasons[code]['count'] += row['count']
            else : 
                coded_reasons[code] = {'count':row['count']}
                concept_ids.append(code)
    concept_ids = tuple(concept_ids)

    rt = ReportTable.objects.get(name='amrs_concept_name')
    parameter_values = (concept_ids,)
    rows = rt.run_report_table(parameter_values=parameter_values,as_dict=True)['rows']              

    reasons = []
    for r in rows:
        reasons.append({'concept_id':r['concept_id'],
                        'name':r['name'],
                        'count':coded_reasons[str(r['concept_id'])]['count']
                        })


    return render(request,'ltfu/reason_missed_appt.html',
                  {'reason_missed_appt':reasons,
                   'start_date':start_date,
                   'end_date':end_date,
                   'location_ids': location_ids_str,
                   'times_asked': times_asked,
                   }
                  )


@login_required
def update_defaulter_cohorts(request):
    if not Authorize.authorize(request.user,['superuser']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    DefaulterCohort.update_defaulter_cohorts()    
    return HttpResponseRedirect('/ltfu/manage_defaulter_cohorts')


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


@login_required
def outreach_worker_defaulter_list(request):
    if not Authorize.authorize(request.user,['outreach_all','outreach_manager','outreach_supervisor','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    cohort_uuid = get_var_from_request(request,'defaulter_cohort_uuid')
    prev_cohort_uuid = request.session.get('cohort_uuid')

    # this means the user is coming from a form submission page, otherwise there should always be a cohort_uuid
    if cohort_uuid is None : cohort_uuid = prev_cohort_uuid

    request.session['cohort_uuid'] = cohort_uuid
    dc = DefaulterCohort.objects.get(cohort_uuid=cohort_uuid)    
 
    if prev_cohort_uuid is not None and prev_cohort_uuid == cohort_uuid: 
        my_defaulter_list = json.loads(request.session.get('my_defaulter_list',''))
    else : my_defaulter_list = []
            
    if my_defaulter_list is None or len(my_defaulter_list) == 0 :
        patient_uuids_in_use = []
        sessions = Session.objects.filter(expire_date__gt=datetime.now())
        print 'num sessions: ' + str(len(sessions))
        for s in sessions:
            print 'user_id: ' + str(request.user.id)
            print 'session owner: ' + str(s.get_decoded().get('_auth_user_id'))
            session_owner_id = s.get_decoded().get('_auth_user_id')
            if session_owner_id is not None and request.user.id != int(session_owner_id):
                decoded = s.get_decoded().get('my_defaulter_list')
                if decoded is not None:
                    defaulters = json.loads(decoded)
                    for d in defaulters:
                        patient_uuids_in_use.append(d['uuid'])


            #3/8/2014: the following is a temporary solution to deleting old sessions. it is NOT in the right place                             
            if session_owner_id is None:
                s.delete()

        my_defaulter_list = dc.get_defaulter_list(patient_uuids_in_use)
        
        request.session['my_defaulter_list'] = json.dumps(my_defaulter_list, cls=DjangoJSONEncoder)

    location = Location.get_location(dc.location_id)
    defaulter_cohorts = DefaulterCohort.objects.all().order_by('name')
    
    return render(request,'ltfu/outreach_worker_defaulter_list.html',
                  {'defaulter_list':my_defaulter_list,
                   'location':location,
                   'defaulter_cohort':dc,
                   'defaulter_cohorts':defaulter_cohorts,
                   }
                  )

    

@login_required
def outreach_form(request):

    if not Authorize.authorize(request.user,['outreach_all','outreach_manager','outreach_supervisor','outreach_worker']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    import requests
    import json
    import amrs_settings

    headers = {'content-type': 'application/json'}
    if request.method == 'GET':
        patient_uuid = request.GET['patient_uuid']        
        location_uuid = request.GET['location_uuid']
        patient = Patient.get_patient_by_uuid(patient_uuid)
        location = Location.get_location_by_uuid_db(location_uuid)

        locations = Location.get_locations()
        encounter_type = EncounterType.get_encounter_type_by_uuid('df5547bc-1350-11df-a1f1-0026b9348838') #outreach
                                                                   
        args = {'patient':patient,
                'encounter_type':encounter_type,
                'location':location,
                'locations':locations
                }
        return render(request,'ltfu/OutreachForm.html',args)
                


    elif request.method == 'POST':        
        patient_uuid = request.POST['patient_uuid']        
        location_uuid = request.POST['location_uuid']
        #location_uuid = '08feae7c-1352-11df-a1f1-0026b9348838'
        dc = DefaulterCohort.objects.get(location_uuid=location_uuid)

        forms = OutreachFormSubmissionLog.objects.filter(patient_uuid=patient_uuid,date_submitted__gte=dc.date_updated)
        # if forms is non-empty, a form was already submitted for this patient today. 
        if forms.count() > 0 :
            pass
            #return HttpResponseRedirect('/ltfu/outreach_worker_defaulter_list')
            

        provider_uuid = '5b6ee21a-1359-11df-a1f1-0026b9348838' #request.POST['provider_uuid']
        encounter_type_uuid = request.POST['encounter_type_uuid']
        encounter_datetime = request.POST['encounter_datetime']
        obs = []

        for key,value in request.POST.iteritems():
            if key.startswith('obs__') and value.strip() != '':
                question_uuid = key[5:]
                l = request.POST.getlist(key)
                for val in l:
                    obs.append({'concept':question_uuid,'value':val})
                


            if key.startswith('attr__') and value.strip() != '':
                attr_type_uuid = key[6:]                
                result = PersonAttribute.create_person_attribute_rest(person_uuid=patient_uuid,person_attribute_type_uuid=attr_type_uuid,value=value)
                

        Encounter.create_encounter_rest(patient_uuid=patient_uuid,
                                        encounter_datetime=encounter_datetime,
                                        location_uuid=location_uuid,
                                        encounter_type_uuid=encounter_type_uuid,
                                        provider_uuid=provider_uuid,
                                        obs=obs)


        #dc = DefaulterCohort.objects.get(location_id=1)
        my_defaulter_list = json.loads(request.session.get('my_defaulter_list',''))
        for d in my_defaulter_list :
            if d['uuid'] == patient_uuid : 
                print 'defaulter list length: ' + str(len(my_defaulter_list))
                my_defaulter_list.remove(d)
                print 'removed element. defaulter list length: ' + str(len(my_defaulter_list))


        request.session['my_defaulter_list'] = json.dumps(my_defaulter_list, cls=DjangoJSONEncoder)


        log = OutreachFormSubmissionLog(patient_uuid=patient_uuid,
                                        location_uuid=location_uuid,
                                        defaulter_cohort_uuid = dc.cohort_uuid,
                                        creator=request.user.id,                                        
                                        )
        log.save()
        return HttpResponseRedirect('/ltfu/outreach_worker_defaulter_list')
        #return render(request,'ltfu/close_tab.html',{}) 
    
    
    
def test(request):
    if not Authorize.authorize(request.user,['superuser']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    patient_uuid='13eaab9a-d51f-42fc-ac89-b1e15f503746'    
    attr_type_uuid = '72a759a8-1359-11df-a1f1-0026b9348838'
    value = '0724000001'
    #result = PersonAttribute.create_person_attribute_rest(patient_uuid,attr_type_uuid,value)
    #result = Patient.get_patient_by_uuid(patient_uuid)

    location1 = Location.get_location_by_uuid('08feae7c-1352-11df-a1f1-0026b9348838')
    location2 = Location.get_location_by_uuid_db('08feae7c-1352-11df-a1f1-0026b9348838')
    result = [location1,location2]


    return render(request,'ltfu/test.html',{'result':result})
