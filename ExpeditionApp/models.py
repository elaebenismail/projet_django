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
    dernier = (cls.objects.filter(reference__startswith=prefixe).order_by('reference').first())
    compteur = (int(dernier.reference[-5:])+1 
    if dernier else 1)
    if compteur > 99999:
        raise ValidationError('limit exceeded')
    return f"{prefixe}{compteur:05d}"

def save(self, *args, **kwargs):
    if not self.reference:
        self.reference = self._generate_ref()
    self.full_clean()
    super().save(*args, **kwargs)