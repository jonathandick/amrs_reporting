from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from amrs_user_validation.models import *
from amrs_interface.models import *
from utilities import *

def access_denied(request) :
    return render(request,'amrs_user_validation/access_denied.html',{})


@login_required
def edit_location_group(request):    
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    group_id = get_var_from_request(request,'location_group_id')
    if group_id : g = DerivedGroup.objects.filter(id=group_id)[0]
    else : g = DerivedGroup()

    if request.method == 'GET':
        l = g.get_base_members()
        existing_member_ids= g.get_member_ids()

        return render(request,'amrs_interface/edit_location_group.html',
                      {'location_group':g,
                       'locations':l,
                       'existing_member_ids':existing_member_ids,
                       }
                      )
    elif request.method == 'POST':
        args = request.POST
        g.set_self(args)
        return HttpResponseRedirect('/amrs_interface/manage_location_groups')
        

@login_required
def delete_location_group(request):    
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    location_group_id = get_var_from_request(request,'location_group_id')
    if location_group_id :
        DerivedGroupMember.objects.filter(derived_group_id=location_group_id).delete()
        DerivedGroup.objects.filter(id=location_group_id).delete()

    return HttpResponseRedirect('/amrs_interface/manage_location_groups')


@login_required
def manage_location_groups(request):    
    if not Authorize.authorize(request.user,['superuser']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    groups = DerivedGroup.objects.filter(base_class='Location')
    locations = Location.get_locations()
    return render(request,'amrs_interface/manage_location_groups.html',
                  {'location_groups':groups,
                   'locations':locations,
                   }
                  )




