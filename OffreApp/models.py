from django.db import models
from django.core.exceptions import ValidationError
from EntreprisesApp.models import Entreprise
from ExpeditionsApp.models import Expedition

def clean(self):
        super().clean()
        # Règle métier 
        if self.entreprise_id and self.entreprise.type_entreprise == 'chargeur':
            raise ValidationError({
                'entreprise': "Une offre ne peut pas être ajoutée par une entreprise de type chargeur."
            })
class Offre(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
    ]

    prix = models.DecimalField(max_digits=10, decimal_places=2)
    delai_jours = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    expedition = models.ForeignKey(
        Expedition,
        on_delete=models.CASCADE,
        related_name='offres',
    )
    transporteur = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='offres',
        limit_choices_to={'type_entreprise': 'transporteur'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

 
