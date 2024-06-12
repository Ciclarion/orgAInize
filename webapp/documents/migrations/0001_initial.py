# Generated by Django 5.0.6 on 2024-05-29 12:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Formation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('nombre_personnes', models.IntegerField()),
                ('frais_inscription', models.DecimalField(decimal_places=2, max_digits=10)),
                ('pre_requis', models.TextField()),
                ('diplome', models.CharField(blank=True, max_length=255, null=True)),
                ('metier', models.CharField(max_length=255)),
                ('syllabus_pdf', models.FileField(blank=True, null=True, upload_to='syllabus/')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=255)),
                ('categorie', models.CharField(choices=[('administrative', 'Administrative'), ('pedagogique', 'Pédagogique'), ('enseignement', 'Enseignement'), ('exercices', 'Exercices'), ('examen_blanc', 'Examen Blanc'), ('intervenants', 'Intervenants'), ('ressources', 'Ressources'), ('foad', 'FOAD'), ('dossier_pro', 'Dossier Professionnel')], max_length=20)),
                ('niveau_acces', models.CharField(choices=[('interne', 'Interne'), ('externe', 'Externe')], max_length=10)),
                ('fichier', models.FileField(upload_to='documents/')),
                ('formation', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='documents.formation')),
            ],
        ),
    ]
