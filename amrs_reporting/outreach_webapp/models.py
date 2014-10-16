from django.db import models
from defaulter_cohort.models import *
import json

# Create your models here.

class CohortCache(models.Model):
    defaulter_cohort_id = models.IntegerField()
    location_uuid = models.CharField(max_length=500,null=True)
    date_modified = models.DateField(auto_now=True)
    json = models.TextField(null=True)

    @staticmethod
    def update_cohort_cache() :
        dcs = DefaulterCohort.objects.filter(retired=0)
        for dc in dcs :
            qs = CohortCache.objects.filter(id=dc.defaulter_cohort_id)
            if qs.count() > 0 :
                cache = qs[0]
            else : cache = CohortCache(defaulter_cohort_id=dc.id,
                                       cohort_uuid = dc.cohort_uuid)
            cache.set_json()



    @staticmethod
    def get_cohort(cohort_id):
        import datetime
        qs = CohortCache.objects.filter(defaulter_cohort_id=cohort_id)
        dc = DefaulterCohort.objects.get(id=cohort_id)
        response = {}
        
        if dc.retired :
            new_dc = DefaulterCohort.objects.filter(location_uuid=dc.location_uuid,retired=0)[0]

            dcs = DefaulterCohort.objects.filter(retired=0).order_by("name")
            cohorts = []
            for dc in dcs :
                cohorts.append({"id":dc.id,"name":dc.name.capitalize()})                
            response['defaulter_cohorts'] = cohorts
            response['messages'] = ["The requested cohort is retired. You have been updated with the most recent " + dc.name]                        
            CohortCache.objects.filter(defaulter_cohort_id=cohort_id).delete()
            cache = CohortCache(defaulter_cohort_id=new_dc.id,
                                location_uuid=new_dc.location_uuid,
                                json = new_dc.get_json())
            cache.save()
        elif qs.count() > 0:
            print "found cached cohort"
            cache = qs[0]
            today = datetime.date.today()            
            if cache.date_modified < today :
                print "cache is old, getting new cohort"
                cache.set_json()

        else :
            try:
                print "writing cohort to cache"
                dc = DefaulterCohort.objects.get(id=cohort_id)
                
                cache = CohortCache(defaulter_cohort_id=cohort_id,
                                    location_uuid = dc.location_uuid,
                                    json = dc.get_json(),
                                    )
                cache.save()
            except Exception, e:
                print "No defaulter cohort exists with id : " + str(cohort_id)
                print e
                return response

        response["defaulter_cohort"] = json.loads(cache.json)
        return json.dumps(response)



    def set_json(self):
        dc = DefaulterCohort.objects.get(id=self.defaulter_cohort_id)
        self.json = dc.get_json()
        self.save()
        

    

