from django.db import models
from django.core.exceptions import ValidationError
from EntrepriseApp.models import Entreprise
from ExpeditionApp.models import Expedition


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

    def clean(self):
        super().clean()
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({
                'transporteur': "Une offre ne peut être créée que par une entreprise de type transporteur."
            })

        if self.transporteur_id and self.vehicule_id and self.vehicule.proprietaire_id != self.transporteur_id:
            raise ValidationError({
                'vehicule': "Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

