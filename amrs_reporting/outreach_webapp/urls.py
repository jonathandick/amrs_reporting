from django.conf.urls import patterns, include, url
import outreach_webapp.views as views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'outreach_webapp'
urlpatterns = patterns('',
                       url(r'^' + app_name + '/?$',views.index),
                       url(r'^' + app_name + '/ajax_update_phone_number/?$',views.ajax_update_phone_number),
                       url(r'^' + app_name + '/ajax_get_defaulter_cohort/?$',views.ajax_get_defaulter_cohort),
                       url(r'^' + app_name + '/ajax_submit_encounter/?$',views.ajax_submit_form),
                       )
                       

