from django.db import models
from django.contrib.auth.models import User                                                                                                             
from datetime import date, time, datetime, timedelta                                                                                                    
from django.db.models import Avg,Min,Max,Count,Q,Sum                                                                                                     
from amrs_interface.models import *
from utilities import *


class Authorize(models.Model):
    
    @staticmethod
    def authorize(user,permitted_roles=None,permitted_locations=None):        
        a = AMRSUser.objects.get(username=user.username)
        

        if permitted_roles is None : return True
        elif a.has_role([RoleType.SUPERUSER_ROLE_TYPE_ID]): return True
        else :
            has_location_privilege = a.has_location_privilege(permitted_locations)
            role_type_ids = RoleType.objects.filter(name__in=permitted_roles).values_list('id',flat=True)
        
            has_role = a.has_role(role_type_ids)
            return (has_role and has_location_privilege)


    @staticmethod
    def get_role_type_ids(role_type_names):
        return RoleType.objects.filter(name__in=role_type_names).values_list('id',flat=True)
        
    

class RoleType(models.Model):
    SUPERUSER_ROLE_TYPE_ID=1    
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    
    def init(self):
        rt = RoleType(name='superuser',description='Has access to all functions')
        rt.save()

        
class Role(models.Model) :    
    user_id = models.IntegerField()
    role_type_id = models.IntegerField()


    def init(self):
        u = AMRSUser.objects.get(username='amrs_reporting')
        r = Role(user_id=u.id,role_type_id=RoleType.SUPERUSER_ROLE_TYPE_ID)
        r.save()


class LocationPrivilege(models.Model):
    ALL_LOCATIONS = -1
    user_id = models.IntegerField()
    location_id = models.IntegerField()

    

class AMRSUser(models.Model):
    
    first_name = models.CharField(max_length=160)
    last_name = models.CharField(max_length=160)
    username = models.CharField(max_length=30)
    email = models.CharField(max_length=100,null=True,blank=True)
    cell_phone_number = models.CharField(max_length=20)
    requires_password_change = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)

    voided = models.BooleanField(default=False)
    date_voided = models.DateTimeField(blank=True,null=True)



    def __unicode__(self):
        return (self.first_name + " " + self.last_name)


    def init(self):        
        a = AMRSUser(first_name='Jonathan',last_name='Dick',email='jonathan.j.dick@gmail.com',username='amrs_reporting',cell_phone_number='+254724679898')
        a.save()
        

    def set_password(self,password) :
        u = User.objects.get(username=self.username)
        u.set_password(password)
        u.save()


    def set_self(self,args) :
        new_user = False
        messages = []
        if self.id is None : 
            new_user = True
            max_allowed_users = 0
        else : 
            prev_username = self.username

        if 'username' in args and args['username'] != '' :
            username = args['username']
            num_users = User.objects.filter(username=username).count()
            if num_users > 1 :
                messages.append('Username is taken. Please choose another username.')
                return messages

        error_free = True
        try : 
            for key,value in args.iteritems() :
                if hasattr(self,key) : setattr(self,key,value)
        except Exception, e:
            print e
            messages.append(e)
            error_free = False

        if error_free :
            self.save()

            if new_user :
                if 'email' not in args or args['email'] is None : email = ''
                else : email = args['email']
                user = User.objects.create_user(username=args['username'], email=email, password=args['password'])
                self.requires_password_change = True
                self.save()
            else :
                user = args['amrs_user_id']
                if 'password' in args and args['password'] != '':
                    self.set_password(args['password'])
                if 'username' in args and args['username'] != '' :
                    user = User.objects.get(username=prev_username)
                    user.username = args['username']
                    user.save()
            
            role_type_id = get_var(args,'role_type_id')
            if role_type_id :
                Role.objects.filter(user_id=self.id).delete()
                r = Role(user_id=self.id,role_type_id=role_type_id)
                r.save()


            location_privilege_ids = args.getlist('location_privilege_ids')
            LocationPrivilege.objects.filter(user_id=self.id).delete()
            for location_id in location_privilege_ids:
                LocationPrivilege(user_id=self.id,location_id=location_id).save()


        return messages



    def delete_self(self) :
        u = User.objects.get(username=self.username)
        if not u.is_superuser :            
            u.delete()
            self.delete()


    def void(self) :
        u = User.objects.get(username=self.username)
        if not u.is_superuser : 
            u.is_active = False
            u.save()
            self.voided = True
            self.save()


    def has_role(self,role_type_ids):
        
        if role_type_ids is None : return True
        return Role.objects.filter(user_id=self.id,role_type_id__in=role_type_ids).exists()

    def get_role_type_names(self):
        role_type_ids = Role.objects.filter(user_id=self.id).values_list('role_type_id',flat=True)
        return ', '.join(RoleType.objects.filter(id__in=role_type_ids).values_list('name',flat=True))



    def has_location_privilege(self,location_ids):
        if location_ids is None : return True
        has_all = LocationPrivilege.objects.filter(user_id=self.id,location_id=-1).exists()
        if has_all : return True
        else : return LocationPrivilege.objects.filter(user_id=self.id,location_id__in=location_ids).exists()
    


    def get_location_privileges(self):
        return LocationPrivilege.objects.filter(user_id=self.id)


    def get_location_privilege_ids(self):
        return LocationPrivilege.objects.filter(user_id=self.id).values_list('location_id',flat=True)
