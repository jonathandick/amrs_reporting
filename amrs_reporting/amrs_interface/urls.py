from django.conf.urls import patterns, include, url
import amrs_interface.views as views
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^amrs_interface/access_denied/?$',views.access_denied),
                       url(r'^amrs_interface/edit_location_group/?$',views.edit_location_group),
                       url(r'^amrs_interface/create_location_group/?$',views.edit_location_group),
                       url(r'^amrs_interface/delete_location_group/?$',views.delete_location_group),                       
                       url(r'^amrs_interface/manage_location_groups/?$',views.manage_location_groups),
                       
                       )
