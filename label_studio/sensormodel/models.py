from django.db import models

class SensorType(models.Model):
    manufacturer = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=50, blank=True)
    version = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.manufacturer + '| ' + self.name + '| ' + self.version

class Sensor(models.Model):
    sensor_id = models.IntegerField()
    description = models.TextField(max_length=100, blank=True)

    sensortype = models.ForeignKey(SensorType,on_delete=models.RESTRICT, null=True, blank=True)

    def __str__(self):
        return 'Sensor: ' + str(self.sensor_id)


class Subject(models.Model):
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    extra_info = models.TextField(max_length=100, blank=True)

    # sensors = models.ForeignKey(Sensor,on_delete=models.RESTRICT,blank=True, null=True) delete

    def __str__(self):
        return 'Subject: ' + self.name


# Deployments are connections of subjects and sensors that are connected to the subject
class Deployment(models.Model): 
    name = models.CharField(max_length=50, blank=True)
    begin_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    location = models.TextField(max_length=50)
    position = models.TextField(max_length=50, blank=True)
    
    sensor = models.ManyToManyField(Sensor,blank=True)
    subject = models.ManyToManyField(Subject,blank=True) 

    sensorlist = models.TextField(max_length=500,blank=True)
    subjectlist = models.TextField(max_length=500,blank =True)

    def CreateLists(self):
        sensList = self.sensor.all()
        for sens in sensList:
            self.sensorlist += str(sens) + ', '
        self.sensorlist = self.sensorlist[:-2]
        subjlist = self.subject.all()
        for subj in subjlist:
            self.subjectlist += str(subj)+ ', '
        self.subjectlist = self.subjectlist[:-2]
        

    def __str__(self):
        return 'Deployment: ' + self.name



