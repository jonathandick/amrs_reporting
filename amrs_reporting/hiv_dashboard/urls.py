from django.conf.urls import patterns, include, url
import hiv_dashboard.views as views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'hiv_dashboard'
urlpatterns = patterns('',
                       url(r'^' + app_name + '/index/?$',views.index),
                       url(r'^' + app_name + '/view_indicators_by_clinic/?$',views.view_indicators_by_clinic),
                       url(r'^' + app_name + '/view_indicators_by_month/?$',views.view_indicators_by_month),                       
                       )
