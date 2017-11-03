from __future__ import absolute_import, unicode_literals
from celery import shared_task

from .apriori import Apriori
from .models import Archivo


# @shared_task
# def async_apriori(minsup, minconf, dataset):
#     apriori(minsup, minconf, dataset)

@shared_task
def async_apriori(minsup, minconf, pk):
    archive = Archivo.objects.get(pk=pk)
    a = Apriori(archive.file, minsup, minconf)
    a.apriori()
