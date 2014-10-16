from django.conf.urls import patterns, include, url
import encounter_form.views as views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'encounter_form'
urlpatterns = patterns('',
                       url(r'^' + app_name + '/view_rest_errors/?$',views.view_rest_errors),
                       url(r'^' + app_name + '/ajax_resubmit_encounter/?$',views.ajax_resubmit_encounter),
                       url(r'^' + app_name + '/resubmit_encounter/?$',views.resubmit_encounter),
                       url(r'^' + app_name + '/delete_encounter_log/?$',views.delete_encounter_log),
                       url(r'^' + app_name + '/edit_encounter/?$',views.edit_encounter),
                       )
