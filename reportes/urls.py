from django.conf.urls import url
from . import views

urlpatterns = [
     url(r'^vendedor/$', views.reporte1, name='reporte1'),
     url(r'^ventas/$', views.reporte2, name='reporte2'),
     url(r'^compras/$', views.reporte3, name='reporte3'),
     url(r'^clientesPorCobrar/$', views.reporte4, name='reporte4'),
     url(r'^informeGeneral/$', views.reporte5, name='reporte5'),
]
