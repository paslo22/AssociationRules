from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^ejecutar/$', views.ejecutar, name='ejecutar'),
    url(r'^popup/$', views.pop_up, name='pop_up'),
    url(r'^estadoTask/$', views.estado_task, name='estado_task'),
    url(r'^$', views.index, name='index'),
]
