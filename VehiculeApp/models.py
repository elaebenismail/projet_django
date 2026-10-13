from django.db import models
from django.core.exceptions import ValidationError  # ←
from EntrepriseApp.models import Entreprise
from django.core.validators import MinValueValidator

class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=11, unique=True)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1, "Capacité doit etre sup à 0kg")])  # ← PositiveIntegerField (TP) + capacité non nulle
    disponible = models.BooleanField(default=True)  # ← était "disponibilite"
    type_vehicule = models.CharField(max_length=20, choices=[  # ← codes du TP
        ('camionnette', 'Camionnette '),
        ('camion_porteur', 'Camion porteur'),
        ('semi_remorque', 'Semi-remorque'),
        ('fourgon', 'Fourgon'),
    ], default='camionnette')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    entreprise = models.ForeignKey(  # ← "entreprise" (nom du TP)
        Entreprise,
        on_delete=models.CASCADE,
        related_name='vehicules',
        limit_choices_to={'type_entreprise': 'transporteur'},  # ←
    )

    def clean(self):  # ← règle métier : entreprise de type transporteur
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({'entreprise': "Un véhicule doit appartenir à une entreprise de type transporteur."})

    def save(self, *args, **kwargs):  # ←
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.immatriculation} - {self.get_type_vehicule_display()}"