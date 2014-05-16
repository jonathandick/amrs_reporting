from django.db import models
import MySQLdb as mdb
import sys
import ast
import settings


# BEGIN Report *****************************************************************************

class Report(models.Model):
    
    name = models.CharField(max_length=160)
    description = models.CharField(max_length=1000,null=True,blank=True)
    template = models.CharField(max_length=1000,null=True,blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    voided = models.BooleanField(default=False)
    date_voided = models.DateTimeField(blank=True,null=True)


    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE


    def create(name=name,description=None):
        self.name = name
        self.description = description
        self.save()
        
        

    # returns a tuple of ('path_to_report_template',dictionary of tables)
    def run_report(self,parameters=None,as_dict=False) :
        con = None
        args = []
        try:
            con = mdb.connect(self.HOST,self.USER,self.PASSWORD,self.DATABASE)
            if as_dict :
                cur = con.cursor(mdb.cursors.DictCursor)
            else : cur = con.cursor()

            report_members = ReportMember.objects.filter(report_id=self.id).order_by('index')
            args = []
            for rm in report_members :
                rt = rm.get_report_table()                
                sql = rt.get_sql()
                if parameters : 
                    parameter_values = rt.get_parameter_values(parameters)
                else : 
                    parameter_values = rm.get_parameter_values()
                    
                cur.execute(sql,parameter_values)
                rows = cur.fetchall()
                cols = cur.description
                args.append({'rm':rm,'cols':cols,'rows':rows})
        except Exception, e:            
            print e
                
        finally:                
            if con:    
                con.close()

        return args
    

    # returns a pdf of the report
    def get_report_as_pdf(self) :
        pass


    def add_report_table(self,report_table_id) :
        rm = ReportMember(report_id=self.id,report_table_id=report_table_id)
        rm.save()

    def remove_report_table(self,report_table_id):
        rm = ReportMember(report_id=self.id,report_table_id=report_table_id)
        rm.delete()



    def add_report_table_parameters(self,report_table_id,parameters):
        rm = ReportMember.objects.get(id=report_table_id)
        rm.set_parameter_values(parameters)

        


# BEGIN ReportTable ************************************************************************

class ReportTable(models.Model):
        
    name = models.CharField(max_length=160)
    description = models.CharField(max_length=1000,null=True,blank=True)
    report_table_sql = models.TextField()

    HOST = settings.HOST
    USER = settings.USER
    PASSWORD = settings.PASSWORD
    DATABASE = settings.DATABASE


    def get_sql(self) :
        return self.report_table_sql


    def get_parameter_values(self,parameters,report_member_id=None):
        values = ()
        rtps = ReportTableParameter.objects.filter(report_table_id = self.id).order_by('index')
        for rtp in rtps :
            values += (rtp.get_parameter_value(parameters,report_member_id),)
        return values

    def get_parameters(self):
        parameters = ReportTableParameter.objects.filter(report_table_id=self.id).order_by('index')
        return parameters


    def get_parameters_s(self):
        parameters = ReportTableParameter.objects.filter(report_table_id=self.id).order_by('index')
        s = ''
        for p in parameters :
            s += p.name + '===' + p.default_value + ';;;'    
        return s[:-3]
            
        
    def create_parameters(self,params,parameter_count) :
        prev_index = 0
        for i in range(parameter_count):
            while True: 
                if 'parameter_name_' + str(prev_index) in params and params['parameter_name_' + str(prev_index)] != '':
                    rp = ReportTableParameter(name=params['parameter_name_' + str(i)],
                                              default_value=params['parameter_default_value_'+str(i)],
                                              index=i,
                                              report_table_id=self.id)
                    
                    rp.save()                    
                    prev_index += 1
                    break    
                
                prev_index += 1

                if prev_index > 20 : 
                    break

    # returns a tuple of (cols,rows)
    # parameters is a dictionary generally obtained from a request object
    # parameter values is a tuple that can be supplied directly for purposes of running the query               
    def run_report_table(self,parameters=None,parameter_values=None,as_dict=False,limit=None) :
        cols = None
        rows = None
        try:
            con = mdb.connect(self.HOST,self.USER,self.PASSWORD,self.DATABASE)
            if as_dict :
                cur = con.cursor(mdb.cursors.DictCursor)
            else : cur = con.cursor()

            if parameter_values is None :
                parameter_values = self.get_parameter_values(parameters)

            print parameter_values
            sql = self.report_table_sql
            if limit : sql += ' limit 0,' + str(limit)
            cur.execute(sql,parameter_values)

            #assume that the last query in the string is the query intended to produce the data table
            rows = cur.fetchall()
            cols = cur.description

        except Exception, e:            
            print e
            print cur._executed
                
        finally:                
            if con:    
                con.close()

        return {'cols':cols,'rows':rows}


# BEGIN ReportTableParameter ******************************************************************

class ReportTableParameter(models.Model):
    
    report_table_id = models.IntegerField()
    name = models.CharField(max_length=160)
    default_value = models.CharField(max_length=300)
    index = models.IntegerField()

    PARAMETER_TYPES = ['string/int','list']

    date_created = models.DateTimeField(auto_now_add=True)

    # NOTE: if a value starts with a '(', it will be assumed to be a list and converted to one
    def get_parameter_value(self,parameters,report_member_id=None) :
        if report_member_id : name = str(report_member_id) + self.name
        else : name = self.name
        
        if parameters and name in parameters and parameters[name] != '' :
            value = parameters[name]
        else :
            value = self.default_value

        if value[0:1] == '(' :
            value = value[1:-1].split(',')

        return value




# BEGIN ReportMember ******************************************************************
            

class ReportMember(models.Model):
    
    name = models.CharField(max_length='300',null=True,blank=True)
    report_id = models.IntegerField()
    report_table_id = models.IntegerField()
    parameter_values = models.TextField(null=True,blank=True)
    index = models.IntegerField()
    title = models.TextField(null=True,blank=True)


    def get_report_table(self) :
        return ReportTable.objects.get(id=self.report_table_id)

    def get_report(self):
        return Report.objects.get(id=self.report_id)


    # return self.parameter_values as tuple. this is required for the query
    def get_parameter_values(self):
        parameter_values = None
        if self.parameter_values :
            print self.parameter_values
            parameter_values = ast.literal_eval(self.parameter_values)
        return parameter_values


    # set the values of this report table for this report
    def set_parameter_values(self,parameters) :
        rt = ReportTable.objects.get(id=self.report_table_id)
        values = rt.get_parameter_values(parameters,self.id)
        if values : self.parameter_values = str(values)

    
        




    



    
