from django.db import models
import MySQLdb as mdb

# Create your models here.


class AmrsDataset(models.Model) :
    dataset_name = models.CharField(max_length=160)
    description = models.CharField(max_length=600)
    sql_file_name = models.CharField(max_length=160)
    

    HOST = 'localhost'
    USER = 'reporting'
    PASSWORD = 'reporting'
    DATABASE = 'reporting'

    def set_self(self, args):
        pass

    def make_dataset(self) :
        try :
            exec('mysql -h ' + self.HOST + ' -u ' + self.USER + ' -p ' + self.PASSWORD
                 + ' --verbose ' + self.DATABASE + ' < derived_tables_sql/' + self.sql_file_name)
        except Exception, e:
            print e
    
            

            
            
    
    
