from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from EntrepriseApp.models import Entreprise
from ExpeditionApp.models import Expedition
from VehiculeApp.models import Vehicule  # ←


class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),  # ← remplace 'en_attente'
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),  # ← présent dans le TP
    ]

    # Règle 7 : poids max (kg) par type de véhicule  # ←
    POIDS_MAX = {
        'camionnette': 1500,
        'fourgon': 3500,
        'camion_porteur': 19000,
        'semi_remorque': 26000,
    }

    prix = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])  # ←
    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])  # ←
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')  # ←
    date_proposition = models.DateField(auto_now_add=True)  # ←
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
    vehicule = models.ForeignKey(  # ← champ manquant
        Vehicule,
        on_delete=models.CASCADE,
        related_name='offres',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        # Règle 1
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({
                'transporteur': "Une offre ne peut être créée que par une entreprise de type transporteur."
            })

        # Règle 2
        if self.transporteur_id and self.vehicule_id and self.vehicule.entreprise_id != self.transporteur_id:  # ← entreprise_id
            raise ValidationError({
                'vehicule': "Le véhicule associé à une offre doit appartenir à la même entreprise que le transporteur."
            })

        # Règle 3  # ←
        if self._state.adding and self.expedition_id and self.expedition.statut != 'publiee':
            raise ValidationError({
                'expedition': "Une expédition ne peut recevoir de nouvelles offres que si son statut est publiée."
            })

        # Règle 4  # ←
        if self.statut == 'proposee' and self.expedition_id and self.transporteur_id:
            if Offre.objects.filter(
                expedition=self.expedition_id,
                transporteur=self.transporteur_id,
                statut='proposee',
            ).exclude(pk=self.pk).exists():
                raise ValidationError("Cette entreprise a déjà une offre proposée sur cette expédition.")

        if self.vehicule_id:
            # Règle 6  # ←
            if self._state.adding and not self.vehicule.disponible:
                raise ValidationError({'vehicule': "Ce véhicule n'est pas disponible."})

            # Règle 7  # ←
            if self.expedition_id:
                poids = self.expedition.poids_kg
                poids_max = self.POIDS_MAX.get(self.vehicule.type_vehicule)
                if (poids_max is not None and poids > poids_max) or poids > self.vehicule.capacite_kg:
                    raise ValidationError({
                        'vehicule': "Ce véhicule n'est pas compatible avec le poids de l'expédition."
                    })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        # Règle 5 : cascade à l'acceptation  # ←
        if self.statut == 'acceptee':
            self.expedition.statut = 'attribuee'
            self.expedition.save()
            Offre.objects.filter(
                expedition=self.expedition, statut='proposee'
            ).exclude(pk=self.pk).update(statut='refusee')
            
    def __str__(self):
        return f"Offre {self.prix} DT - {self.transporteur} sur {self.expedition.reference} ({self.statut})"