from django.shortcuts import render
from django.http import HttpResponseBadRequest, JsonResponse

from celery.result import AsyncResult
from celery import current_task, signals

from .tasks import async_apriori
from .models import Archivo

from datetime import datetime


def index(request):
    return render(request, 'web/index.html')


def ejecutar(request):
    minconf = request.POST.get('minconf', None)
    minsup = request.POST.get('minsup', None)
    file = request.FILES.get('filename', None)
    if not minconf or not minsup or not file:
        return HttpResponseBadRequest()
    if request.method == 'POST':
        f = Archivo(file=file)
        f.save()
        task = async_apriori.delay(
            float(minsup),
            float(minconf),
            f.pk,
        )
    return JsonResponse({
        'task_id': task.id,
        'filename': file.name,
        'minsup': minsup,
        'minconf': minconf,
    })


def estado_task(request):
    task_id = request.GET.get('task_id', False)
    if not task_id:
        return HttpResponseBadRequest()
    task = AsyncResult(task_id)
    return JsonResponse({
        'status': task.status,
        'info': task.info,
    })


def pop_up(request):
    task = request.GET.get('task_id', False)
    filename = request.GET.get('filename', False)
    minsup = request.GET.get('minsup', False)
    minconf = request.GET.get('minconf', False)
    if not task:
        return HttpResponseBadRequest()
    return render(request, 'web/pop-up.html', {
        'task_id': task,
        'filename': filename,
        'minsup': minsup,
        'minconf': minconf,
    })


@signals.task_prerun.connect
def statsd_task_prerun(**kwargs):
    current_task.start_time = datetime.now()
