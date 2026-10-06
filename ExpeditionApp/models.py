from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone

from EntrepriseApp.models import Entreprise


class Expedition(models.Model):
    STATUT_CHOICES = [
        ('publiee', 'Publiée'),
        ('attribuee', 'Attribuée'),
        ('en_cours', 'En cours'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    reference = models.CharField(max_length=20, unique=True, editable=False)
    ville_depart = models.CharField(max_length=100)
    ville_arrivee = models.CharField(max_length=100)
    poids_kg = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        validators=[MinValueValidator(0.001, 'le poids doit être supérieur à 0kg')],
    )
    date_souhaitee = models.DateField()
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='publiee')
    chargeur = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name='expeditions',
        limit_choices_to={'type_entreprise': 'chargeur'},
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


def clean(self):
    super().clean()
    #regle metier
    if self.entreprise_id and self.entreprise.type_entreprise != 'chargeur':
        raise ValidationError({'entreprise': "une expedition ne peut etre cree que par une entreprise de type chargeur"})

@classmethod
def _generate_ref(cls):
    annee = timezone.now().strftime('%y') #extraire lannee
    prefixe = f"EXP_{annee}_"
    compteur = cls.objects.filter(reference__startswith=prefixe).order_by('reference').last()