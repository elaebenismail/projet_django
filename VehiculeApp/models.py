from django.db import models

# Create your models here.
class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=11, unique=True)
    capacite_kg = models.IntegerField()
    disponibilite = models.BooleanField(default=True)
    type_vehicule = models.CharField(max_length=20, choices=[
        ('camionette','Camionette'),
        ('remorque', 'Semi-Remorque'),
        ('fourgon','Fourgon'),
        ('porteur', 'Porteur'),
    ],default='camionette')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    proprietaire = models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='vehicules')