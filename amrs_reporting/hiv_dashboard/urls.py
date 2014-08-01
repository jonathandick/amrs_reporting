from django.conf.urls import patterns, include, url
import hiv_dashboard.views as views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'hiv_dashboard'
urlpatterns = patterns('',
                       url(r'^' + app_name + '/index/?$',views.index),
                       
                       )
