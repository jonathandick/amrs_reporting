from django.conf.urls import patterns, include, url
import amrs_user_validation.views as views
from django.conf.urls.static import static
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^amrs_user_validation/?$',views.index),
                       url(r'^amrs_user_validation/access_denied/?$',views.access_denied),
                       url(r'^amrs_user_validation/login/?$',views.my_login),                       
                       url(r'^amrs_user_validation/logout/?$',views.my_logout),                       
                       url(r'^amrs_user_validation/create_amrs_user/?$',views.create_amrs_user),
                       url(r'^amrs_user_validation/manage_amrs_users/?$',views.manage_amrs_users),
                       url(r'^amrs_user_validation/delete_amrs_user/?$',views.delete_amrs_user),
                       url(r'^amrs_user_validation/edit_amrs_user/?$',views.edit_amrs_user),
                       )
