from django.db import models
from django.core.exceptions import ValidationError
from EntrepriseApp.models import Entreprise
from django.core.validators import MinValueValidator


class Vehicule(models.Model):
    TYPE_CHOICES = [
        ('camionnette', 'Camionnette / utilitaire léger'),
        ('camion_porteur', 'Camion porteur'),
        ('semi_remorque', 'Semi-remorque'),
        ('fourgon', 'Fourgon'),
    ]

    # Poids maximal (kg) transportable par type de véhicule (règle métier 7), utilisé aussi par Offre
    POIDS_MAX_PAR_TYPE = {
        'camionnette': 1500,
        'fourgon': 3500,
        'camion_porteur': 19000,
        'semi_remorque': 26000,
    }

    immatriculation = models.CharField(max_length=11, unique=True)
    capacite_kg = models.PositiveIntegerField(validators=[MinValueValidator(1, "Capacité doit etre sup à 0kg")])
    disponible = models.BooleanField(default=True)
    type_vehicule = models.CharField(max_length=20, choices=TYPE_CHOICES, default='camionnette')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='vehicules',
        limit_choices_to={'type_entreprise': 'transporteur'},
    )

    def clean(self):
        # Si un champ est vide ou invalide, Django affiche déjà l'erreur : on s'arrête ici
        if not self.entreprise_id or not self.capacite_kg or self.type_vehicule not in self.POIDS_MAX_PAR_TYPE:
            return
        # Règle métier : l'entreprise doit être de type transporteur
        if self.entreprise.type_entreprise != 'transporteur':
            raise ValidationError({'entreprise': "Un véhicule doit appartenir à une entreprise de type transporteur."})
        # La capacité ne doit pas dépasser le maximum de son type
        if self.capacite_kg > self.POIDS_MAX_PAR_TYPE[self.type_vehicule]:
            raise ValidationError({'capacite_kg': "La capacité dépasse le maximum autorisé pour ce type de véhicule."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.immatriculation} - {self.get_type_vehicule_display()}"