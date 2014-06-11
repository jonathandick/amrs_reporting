from django.conf.urls import patterns, include, url
import ltfu.views as views
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()
app_name = 'ltfu'
urlpatterns = patterns('',
                       url(r'^' + app_name + '/index/?$',views.index),
                       url(r'^' + app_name + '/ltfu_ampath/?$',views.ltfu_ampath),
                       url(r'^' + app_name + '/ltfu_clinics/?$',views.ltfu_clinics),
                       url(r'^' + app_name + '/ltfu_clinic/?$',views.ltfu_clinic),
                       url(r'^' + app_name + '/ltfu_by_range/?$',views.ltfu_by_range),
                       url(r'^' + app_name + '/ltfu_get_defaulter_list/?$',views.ltfu_get_defaulter_list),
                       url(r'^' + app_name + '/view_indicators_by_clinic/?$',views.view_indicators_by_clinic),
                       url(r'^' + app_name + '/view_indicators_by_provider/?$',views.view_indicators_by_provider),
                       url(r'^' + app_name + '/view_outreach_worker_forms_done/?$',views.view_outreach_worker_forms_done),
                       url(r'^' + app_name + '/view_data_entry_forms_done/?$',views.view_data_entry_forms_done),
                       url(r'^' + app_name + '/view_reason_missed_appt/?$',views.view_reason_missed_appt),
                       )
