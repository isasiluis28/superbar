from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.

class ControlHorario(models.Model):
	usuario = models.ForeignKey("auth.User")
	fecha = models.DateField(default=timezone.now)
	horario_entrada = models.TimeField(default=timezone.now)
	horario_salida = models.TimeField(blank=True, null=True)

