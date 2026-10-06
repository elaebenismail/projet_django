from django.db import models
from EntrepriseApp.models import Entreprise
from django.core.validators import MinValueValidator

# Create your models here.
class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=11, unique=True)
    capacite_kg = models.IntegerField(validators=[MinValueValidator(100, "Capacité doit etre sup à 100kg")])
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