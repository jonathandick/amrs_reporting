from django.db import models

# Create your models here.

from django.db import models
import MySQLdb as mdb


class Location(models.Model):

    HOST = 'localhost'
    USER = 'reporting'
    PASSWORD = 'reporting'
    DATABASE = 'reporting'
    
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

            
        
        
        
        
