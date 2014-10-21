from django.conf.urls import patterns, include, url
import defaulter_cohort.views as views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'defaulter_cohort'
urlpatterns = patterns('',
                       url(r'^' + app_name + '/update_defaulter_cohorts/?$',views.update_defaulter_cohorts),
                       )
