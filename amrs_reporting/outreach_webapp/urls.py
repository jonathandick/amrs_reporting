from django.conf.urls import patterns, include, url
import outreach_webapp.views as views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'outreach'
urlpatterns = patterns('',
                       url(r'^' + app_name + '/?$',views.index),
                       url(r'^' + app_name + '/ajax_update_phone_number/?$',views.ajax_update_phone_number),
                       url(r'^' + app_name + '/ajax_get_defaulter_cohort/?$',views.ajax_get_defaulter_cohort),
                       url(r'^' + app_name + '/ajax_update_defaulter_cohort/?$',views.ajax_update_defaulter_cohort),
                       url(r'^' + app_name + '/ajax_get_retired_members/?$',views.ajax_get_retired_members),
                       url(r'^' + app_name + '/ajax_get_new_defaulter_cohort/?$',views.ajax_get_new_defaulter_cohort),
                       url(r'^' + app_name + '/ajax_submit_encounter/?$',views.ajax_submit_encounter),
                       url(r'^' + app_name + '/ajax_patient_search/?$',views.ajax_patient_search),
                       url(r'^' + app_name + '/ajax_get_patient/?$',views.ajax_get_patient),
                       url(r'^' + app_name + '/ajax_get_outreach_providers/?$',views.ajax_get_outreach_providers),
                       url(r'^' + app_name + '/ajax_get_locations/?$',views.ajax_get_locations),
                       url(r'^' + app_name + '/ajax_get_defaulter_cohorts/?$',views.ajax_get_defaulter_cohorts),
                       url(r'^' + app_name + '/ajax_update_cohort_cache/?$',views.ajax_update_cohort_cache),
                       url(r'^' + app_name + '/ajax_is_defaulter_cohort_retired/?$',views.ajax_is_defaulter_cohort_retired),
                       url(r'^' + app_name + '/ajax_get_encounter_data/?$',views.ajax_get_encounter_data),
                       url(r'^' + app_name + '/ajax_get_encounter_full/?$',views.ajax_get_encounter_full),
                       url(r'^' + app_name + '/test/?$',views.test),
                       url(r'^' + app_name + '/update_datasets/?$',views.update_datasets),
                       url(r'^' + app_name + '/login/?$',views.angular_login),
                       )
                       

