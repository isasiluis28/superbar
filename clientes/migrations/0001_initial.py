# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-03-22 11:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Barrio',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Ciudad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Ciudad')),
            ],
            options={
                'verbose_name': 'Ciudad',
                'verbose_name_plural': 'Ciudades',
            },
        ),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ruc', models.CharField(max_length=20, unique=True)),
                ('nombre', models.CharField(max_length=50, verbose_name='Nombre o Razon Social')),
                ('telefono', models.CharField(blank=True, max_length=50)),
                ('contacto', models.CharField(blank=True, help_text='Persona con la que establecio contacto en el predio.', max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('direccion', models.CharField(blank=True, max_length=50)),
                ('fecha_ult_compra', models.DateField(blank=True, null=True, verbose_name='Fecha de ultima venta')),
                ('last_cantidad', models.IntegerField(blank=True, null=True, verbose_name='Ultima cantidad vendida')),
                ('barrio', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='clientes.Barrio')),
            ],
            options={
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Proveedor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50, verbose_name='Nombre o Razon Social')),
                ('ruc', models.CharField(max_length=20, unique=True)),
                ('direccion', models.CharField(blank=True, max_length=50)),
                ('telefono', models.CharField(blank=True, max_length=50)),
                ('contacto', models.CharField(blank=True, help_text='Persona con la que establecio contacto.', max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
            ],
            options={
                'verbose_name': 'Proveedor',
                'verbose_name_plural': 'Proveedores',
            },
        ),
        migrations.CreateModel(
            name='Segmento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name': 'Segmento',
                'verbose_name_plural': 'Segmentos',
            },
        ),
        migrations.CreateModel(
            name='Vendedor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('margen_venta', models.FloatField(blank=True, null=True)),
                ('margen_delivery', models.FloatField(blank=True, null=True)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Vendedor',
                'verbose_name_plural': 'Vendedores',
            },
        ),
        migrations.AddField(
            model_name='cliente',
            name='segmento',
            field=models.ForeignKey(blank=True, help_text='Indica un tipo de cliente. Ej: Gimnasio, Particular, etc.', null=True, on_delete=django.db.models.deletion.CASCADE, to='clientes.Segmento', verbose_name='Segmento'),
        ),
        migrations.AddField(
            model_name='cliente',
            name='vendedor',
            field=models.ForeignKey(blank=True, help_text='vendedor al quecorresponde el cliente.', null=True, on_delete=django.db.models.deletion.CASCADE, to='clientes.Vendedor'),
        ),
        migrations.AddField(
            model_name='barrio',
            name='ciudad',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.Ciudad'),
        ),
    ]