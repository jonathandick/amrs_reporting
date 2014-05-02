from django.db import models

# Create your models here.

from django.db import models
import MySQLdb as mdb
import report.settings as settings

class Location(models.Model):

    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE
    
    def get_locations(self):
        locations = {}
        con = None
        try :
            sql = 'select location_id, name from amrs.location'
            con = mdb.connect(self.HOST,self.USER,self.PASSWORD,self.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql)
            locations = cur.fetchall()
        except Exception, e:
            print e

        finally:
            if con : con.close()

        return locations



    def get_location(self, location_id) :
        location = {}
        con = None
        try :
            sql = 'select location_id, name from amrs.location where location_id=%s'
            con = mdb.connect(self.HOST,self.USER,self.PASSWORD,self.DATABASE)
            cur = con.cursor(mdb.cursors.DictCursor)
            cur.execute(sql,(location_id,))
            location = cur.fetchone()
        except Exception, e:
            print e
            
        finally:
            if con : con.close()

        return location

            
        
class Provider(models.model)
        
    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE
    
    def get_outreach_providers(self):
        providers = {}
        con = None
        try :
            sql = 'select t1.provider_id, given_name, family_name from flat_outreach_data t1 join amrs.person_name t2 on t1.provider_id=t2.person_id group by t1.provider_id'
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
        
