from django.db import models
import MySQLdb as mdb
import report.settings as settings
from report.models import *
from utilities import *

class Location(models.Model):

    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE
    

    @staticmethod
    def get_all(retired=0):
        print 'get_all() .......'
        locations = {}
        con = None        
        try :
            sql = 'select location_id, name from amrs.location where retired=' + str(retired) + ' order by name'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            locations = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()
        
        return locations


    @staticmethod
    def get_names(retired=0,subset=None):
        names = {}
        con = None
        try :
            sql = 'select name from amrs.location where retired=' + str(retired)
            if subset: sql += ' and location_id in ' + subset
            sql += ' order by name'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            names = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()
        return names



    @staticmethod
    def get_locations(retired=0):
        locations = {}
        con = None
        try :
            sql = 'select location_id, name from amrs.location where retired=' + str(retired) + ' order by name'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            locations = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return locations


    @staticmethod
    def get_location(location_id) :
        location = {}
        con = None
        try :
            sql = 'select location_id, name from amrs.location where location_id=%s'
            con = mdb.connect(Location.HOST,Location.USER,Location.PASSWORD,Location.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(location_id,))
            location = cur.fetchone()
        except Exception, e:
            print e
            
        finally:
            if con : con.close()

        return location


                       
class Provider(models.Model):
        
    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE
    

    def get_all(self):
        providers = {}
        con = None
        try :
            sql = 'select t1.provider_id, given_name, family_name from flat_outreach_data t1 join amrs.person_name t2 on t1.provider_id=t2.person_id'
            sql += ' group by t1.provider_id order by family_name, given_name'
            con = mdb.connect(self.HOST,self.USER,self.PASSWORD,self.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            providers = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return providers



    def get_outreach_providers(self):
        providers = {}
        con = None
        try :
            sql = 'select t1.provider_id, given_name, family_name from flat_outreach_data t1 join amrs.person_name t2 on t1.provider_id=t2.person_id'
            sql += ' group by t1.provider_id order by family_name, given_name'
            con = mdb.connect(self.HOST,self.USER,self.PASSWORD,self.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            providers = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return providers



    def get_provider_name(self, provider_id) :
        provider = {}
        con = None
        try :
            sql = 'select person_id as provider_id,given_name,family_name from amrs.person_name where person_id=% and voided=0'
            con = mdb.connect(self.HOST,self.USER,self.PASSWORD,self.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(provider_id,))
            location = cur.fetchone()
        except Exception, e:
            print e
            
        finally:
            if con : con.close()

        return provider


    def get_outreach_worker_indicators(self,provider_id):
        rt = ReportTable.objects.filter(name='outreach_worker_indicators')[0]
        outreach_worker_indicators = rt.run_report_table(as_dict=True)['rows']
        return outreach_worker_indicators


class DerivedGroup(models.Model):
    
    name = models.CharField(max_length=200)
    base_class = models.CharField(max_length=200)

    description = models.CharField(max_length=500)


    def get_base_members(self):
        return (globals()[self.base_class]).get_all()


    def get_base_class(self):
        return globals()[self.base_class]
        

    def is_member(self,member_id):
        members = DerivedGroupMember.objects.filter(id=self.id,member_id=member_id)
        return len(members) > 0


    def get_members(self):
        return DerivedGroupMember.objects.filter(derived_group_id=self.id)
    
    def get_member_ids(self):
        return DerivedGroupMember.objects.filter(derived_group_id=self.id).values_list('member_id',flat=True)

    def get_member_names(self):
        c = self.get_base_class()
        ids = self.get_member_ids()
        ids = '(' + ','.join(str(id) for id in ids) + ')'
        return c.get_names(subset=ids)
        


    def set_self(self,args):
        name = get_var(args,'name')
        base_class = get_var(args,'base_class')
        description = get_var(args,'description')
        members = args.getlist('members')
        member_ids = get_var(args,'member_ids')

        if name and base_class and (members or member_ids):
            self.name = name
            self.base_class = base_class
            self.description = description
            self.save()
            
            DerivedGroupMember.objects.filter(derived_group_id=self.id).delete()
            if member_ids :
                member_ids = member_ids.replace(' ','').split(',')
            else : member_ids = members
            
            for member_id in member_ids :
                dg = DerivedGroupMember(derived_group_id=self.id,member_id=member_id)
                dg.save()

                    

class DerivedGroupMember(models.Model):
    derived_group_id = models.IntegerField()
    member_id = models.IntegerField()
    
