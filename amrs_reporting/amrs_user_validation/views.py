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
def index(request):    
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    return my_login(request) #render(request,'amrs_user_validation/index.html',{})


def my_login(request):
    if request.method == 'POST' :        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active: 
                login(request,user)
                request.session.set_expiry(3600)
                return HttpResponseRedirect('../')
            else : error = 'User is not active.'
        else : error = 'Username and password do not match'
        return render(request,'amrs_user_validation/login.html',
                      {'error' : error}
                      )

    else :
        device = get_device(request)
        if device['is_mobile']: return render(request,'amrs_user_validation/mobile_login.html',{})            
        else : return render(request,'amrs_user_validation/mobile_login.html',{})


@login_required
def my_logout(request):
    logout(request)
    return render(request,'amrs_user_validation/login.html',{})

    
@login_required
def create_amrs_user(request):
    if not Authorize.authorize(request.user,['admin']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')        

    if request.method == 'POST' :            
        a = AMRSUser()
        messages = a.set_self(request.POST)            
        if len(messages) > 0 : 
            return render(request,'amrs_user_validation/create_user.html',
                          {'messages':messages})
        else :
            return HttpResponseRedirect('/amrs_user_validation/manage_amrs_users')
    else : 
        rts = RoleType.objects.all()
        locations = Location.get_all()

        return render(request,'amrs_user_validation/create_user.html',
                      {'role_types':rts,
                       'locations':locations,
                       })
        

            

@login_required
def edit_amrs_user(request):
    if not Authorize.authorize(request.user,['admin']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')       
        
    if request.method == 'POST' :
        amrs_user_id = request.POST['amrs_user_id']
        a = AMRSUser.objects.get(id=amrs_user_id)
        messages = a.set_self(request.POST)            
        if len(messages) > 0 : 
            return render(request,'amrs_user_validation/edit_user.html',
                          {'messages':messages})
        else :
            return HttpResponseRedirect('/amrs_user_validation/manage_amrs_users')
    else : 
        amrs_user_id = request.GET['amrs_user_id']
        a = AMRSUser.objects.get(id=amrs_user_id)
        role_type_id=-1
        roles = Role.objects.filter(user_id=a.id)
        locations = Location.get_all()
        location_privilege_ids = a.get_location_privilege_ids()

        if len(roles) > 0 : role_type_id = roles[0].role_type_id

        rts = RoleType.objects.all()
        return render(request,'amrs_user_validation/edit_user.html',
                      {'amrs_user':a,
                       'role_type_id':role_type_id,
                       'role_types':rts,
                       'locations':locations,
                       'location_privilege_ids':location_privilege_ids
                       }
                      )            
            

    


@login_required
def delete_amrs_user(request):
    if not Authorize.authorize(request.user,['admin']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    amrs_user_id = request.GET['amrs_user_id']
    a = AMRSUser.objects.get(id=amrs_user_id)        
    a.delete_self()

    return HttpResponseRedirect('/amrs_user_validation/manage_amrs_users')



@login_required
def manage_amrs_users(request):
    if not Authorize.authorize(request.user,['admin']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    amrs_users = AMRSUser.objects.all()
    return render(request,'amrs_user_validation/manage_users.html',
                  {'amrs_users':amrs_users,
                   })

                      


@login_required
def manage_role_types(request):
    if not Authorize.authorize(request.user,['superuser']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    if request.method == 'GET':
        rts = RoleType.objects.all()
        return render(request,'amrs_user_validation/manage_role_types.html',
                      {'role_types':rts,
                       }
                      )

@login_required
def edit_role_type(request):
    if not Authorize.authorize(request.user,['superuser']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')
    
    rt_id = get_var_from_request(request,'role_type_id')
    if rt_id : rt = RoleType.objects.get(id=rt_id)    
    else : rt = RoleType()

    name = get_var_from_request(request,'name')
    description = get_var_from_request(request,'description')
    
    if name and description :
        
        rt.name=name
        rt.description=description
        rt.save()

    rts = RoleType.objects.all()
    return render(request,'amrs_user_validation/manage_role_types.html',
                  {'role_types':rts,
                   })

@login_required
def delete_role_type(request):
    if not Authorize.authorize(request.user,['superuser']) :
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    rt_id = get_var_from_request(request,'role_type_id')

    if rt_id!=RoleType.SUPERUSER_ROLE_TYPE_ID : 
        if rt_id :
            Role.objects.filter(role_type_id=rt_id).delete()
            RoleType.objects.get(id=rt_id).delete()
        
    rts = RoleType.objects.all()

    return render(request,'amrs_user_validation/manage_role_types.html',
                  {'role_types':rts,
                   })

    


def manage_roles(request):
    pass

@login_required
def manage_location_groups(request):
    pass

