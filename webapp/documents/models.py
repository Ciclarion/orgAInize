from django.db import models
from django.utils import timezone

class Formation(models.Model):
    nom = models.CharField(max_length=255)
    date = models.DateField()
    nombre_personnes = models.IntegerField()
    frais_inscription = models.DecimalField(max_digits=10, decimal_places=2)
    pre_requis = models.TextField()
    diplome = models.CharField(max_length=255, null=True, blank=True)
    metier = models.CharField(max_length=255)
    syllabus_pdf = models.FileField(upload_to='syllabus/', null=True, blank=True)
    date_upload = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.nom

class Document(models.Model):
    CATEGORIE_CHOICES = (
        ('administrative', 'Administrative'),
        ('pedagogique', 'Pédagogique'),
    )
    SOUS_CATEGORIE_CHOICES = (
        ('enseignement', 'Enseignement'),
        ('exercices', 'Exercices'),
        ('examen_blanc', 'Examen Blanc'),
        ('intervenants', 'Intervenants'),
        ('ressources', 'Ressources'),
        ('foad', 'FOAD'),
        ('dossier_pro', 'Dossier Professionnel'),
    )
    ACCES_CHOICES = (
        ('interne', 'Interne'),
        ('externe', 'Externe'),
    )
    formation = models.ForeignKey(Formation, on_delete=models.CASCADE, null=True, blank=True)
    nom = models.CharField(max_length=255)
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES)
    sous_categorie = models.CharField(max_length=20, choices=SOUS_CATEGORIE_CHOICES, null=True, blank=True)
    niveau_acces = models.CharField(max_length=10, choices=ACCES_CHOICES)
    fichier = models.FileField(upload_to='documents/')
    date_upload = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.sous_categorie = self.sous_categorie if self.categorie == 'pedagogique' else None
        super().save(*args, **kwargs)
