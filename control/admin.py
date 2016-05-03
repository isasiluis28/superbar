from django.contrib import admin
from control.models import ControlHorario

# Register your models here.

class ControlHorarioAdmin(admin.ModelAdmin):
	list_display = ("fecha", "usuario", "horario_entrada", "horario_salida")

admin.site.register(ControlHorario, ControlHorarioAdmin)
