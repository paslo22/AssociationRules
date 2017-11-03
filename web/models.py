from django.db import models


class Archivo(models.Model):
    file = models.FileField(upload_to='archives/')
