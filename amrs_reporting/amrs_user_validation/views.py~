from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from amrs_user_validation.models import Authorize, AMRSUser


def access_denied(request) :
    return render(request,'amrs_user_validation/access_denied.html',{})


@login_required
def index(request):    
    if not Authorize.authorize(request.user,['admin']) :        
        return HttpResponseRedirect('/amrs_user_validation/access_denied')

    return render(request,'amrs_user_validation/index.html',{})


def my_login(request):
    if request.method == 'POST' :        
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active: 
                login(request,user)
                return HttpResponseRedirect('../')
            else : error = 'User is not active.'
        else : error = 'Username and password do not match'

        return render(request,'amrs_user_validation/login.html',
                      {'error' : error}
                      )

    else :
        return render(request,'amrs_user_validation/login.html',{})


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
        return render(request,'amrs_user_validation/create_user.html',{})
        

            

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
        return render(request,'amrs_user_validation/edit_user.html',
                      {'amrs_user':a}
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
    return render(request,'amrs_user_validation/manage_users.html',{'amrs_users':amrs_users})
                      

