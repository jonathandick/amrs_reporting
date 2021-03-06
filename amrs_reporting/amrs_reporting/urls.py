from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
import amrs_reports.views as views
import ltfu.views as ltfu_views
import amrs_user_validation.urls as amrs_user_validation_urls
import amrs_interface.urls as amrs_interface_urls
import ltfu.urls as ltfu_urls
import amrs_user_validation.views as amrs_user_validation_views
import hiv_dashboard.urls as hiv_dashboard_urls
import outreach_webapp.urls as outreach_webapp_urls
import outreach_webapp.views as outreach_webapp_views

import encounter_form.urls as encounter_form_urls
import encounter_form.views as encounter_form_views

import defaulter_cohort.urls as defaulter_cohort_urls
import defaulter_cohort.views as defaulter_cohort_views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
                       url(r'^/?$', outreach_webapp_views.index),
                       url(r'^amrs_reports/manage_reports/?$',views.manage_reports),                       
                       url(r'^amrs_reports/manage_report_tables/?$',views.manage_report_tables),                       
                       url(r'^amrs_reports/create_report_table/?$',views.create_report_table),                       
                       url(r'^amrs_reports/delete_report_table/?$',views.delete_report_table),                       
                       url(r'^amrs_reports/run_report_table/?$',views.run_report_table),
                       url(r'^amrs_reports/create_report/?$',views.create_report),                       
                       url(r'^amrs_reports/delete_report/?$',views.delete_report),                       
                       url(r'^amrs_reports/run_report/?$',views.run_report),
                       url(r'^amrs_reports/get_report_as_pdf/?$',views.get_report_as_pdf),
                       url(r'^amrs_reports/update_datasets/?$',views.update_datasets),
                       url(r'^amrs_reports/view_sync_stats/?$',views.view_sync_stats),                       
                       ) 
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 
urlpatterns += amrs_user_validation_urls.urlpatterns 
urlpatterns += amrs_interface_urls.urlpatterns
urlpatterns += ltfu_urls.urlpatterns
urlpatterns += hiv_dashboard_urls.urlpatterns
urlpatterns += outreach_webapp_urls.urlpatterns
urlpatterns += encounter_form_urls.urlpatterns
urlpatterns += defaulter_cohort_urls.urlpatterns



