from django.db import models
from django.contrib.auth.models import User                                                                                                             
from datetime import date, time, datetime, timedelta                                                                                                    
from django.db.models import Avg,Min,Max,Count,Q,Sum                                                                                                     

# Create your models here.


class Authorize(models.Model):
    
    @staticmethod
    def authorize(user,permitted_roles):
        print 'authorizing : ' + user.username
        a = AMRSUser.objects.get(username=user.username)
        print a.role
        return a.role in permitted_roles

class Role(models.Model) :    
    user_id = models.IntegerField()
    role = models.CharField(max_length=300)


class AMRSUser(models.Model):
    
    first_name = models.CharField(max_length=160)
    last_name = models.CharField(max_length=160)
    username = models.CharField(max_length=30)
    email = models.CharField(max_length=100,null=True,blank=True)
    cell_phone_number = models.CharField(max_length=20)
    role = models.CharField(max_length=160)
    requires_password_change = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True)

    voided = models.BooleanField(default=False)
    date_voided = models.DateTimeField(blank=True,null=True)



    def __unicode__(self):
        return (self.first_name + " " + self.last_name)


    def init(self):        
        a = AMRSUser(first_name='Jonathan',last_name='Dick',email='jonathan.j.dick@gmail.com',username='jdick',cell_phone_number='+254724679898')
        a.save()
        

    def set_password(self,password) :
        u = User.objects.get(username=self.username)
        u.set_password(password)
        u.save()


    def set_self(self,args) :
        new_user = False
        max_allowed_users = 1
        messages = []
        if self.id is None : 
            new_user = True
            max_allowed_users = 0
        else : 
            prev_username = self.username

        if 'username' in args and args['username'] != '' :
            username = args['username']
            num_users = User.objects.filter(username=username).count()
            if num_users > max_allowed_users :
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
