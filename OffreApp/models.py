from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from EntrepriseApp.models import Entreprise
from ExpeditionApp.models import Expedition
from VehiculeApp.models import Vehicule


class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),
    ]

    prix = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    delai_jours = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')
    date_proposition = models.DateField(auto_now_add=True)
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
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.CASCADE,
        related_name='offres',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        # Si une relation manque, Django affiche déjà « champ obligatoire »
        if not self.expedition_id or not self.transporteur_id or not self.vehicule_id:
            return

        nouvelle = self._state.adding

        # Règle 1
        if self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({'transporteur': "Une offre ne peut être créée que par une entreprise de type transporteur."})

        # Règle 2
        if self.vehicule.entreprise_id != self.transporteur_id:
            raise ValidationError({'vehicule': "Le véhicule doit appartenir à la même entreprise que le transporteur."})

        # Règle 3
        if nouvelle and self.expedition.statut != 'publiee':
            raise ValidationError({'expedition': "Cette expédition n'accepte plus d'offres (elle n'est plus publiée)."})

        # Règle 4
        if self.statut == 'proposee' and Offre.objects.filter(
            expedition_id=self.expedition_id, transporteur_id=self.transporteur_id, statut='proposee'
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Cette entreprise a déjà une offre proposée sur cette expédition.")

        # Une seule offre acceptée par expédition
        if self.statut == 'acceptee' and Offre.objects.filter(
            expedition_id=self.expedition_id, statut='acceptee'
        ).exclude(pk=self.pk).exists():
            raise ValidationError("Cette expédition a déjà une offre acceptée.")

        # Règle 6
        if nouvelle and not self.vehicule.disponible:
            raise ValidationError({'vehicule': "Ce véhicule n'est pas disponible."})

        # Règle 7 : compatibilité type de véhicule / poids
        poids = self.expedition.poids_kg
        type_v = self.vehicule.type_vehicule
        poids_max = Vehicule.POIDS_MAX_PAR_TYPE.get(type_v)
        if poids_max is not None and poids > poids_max:
            raise ValidationError({'vehicule': "Ce type de véhicule ne peut pas transporter le poids de cette expédition."})
        if type_v == 'camion_porteur' and poids < 3500:
            raise ValidationError({'vehicule': "Un camion porteur est adapté aux expéditions de 3,5 à 19 t."})
        if type_v == 'semi_remorque' and poids < 19000:
            raise ValidationError({'vehicule': "Une semi-remorque est adaptée aux expéditions de 19 à 26 t."})
        if poids > self.vehicule.capacite_kg:
            raise ValidationError({'vehicule': "Le poids de l'expédition dépasse la capacité du véhicule."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        # Règle 5 : cascade à l'acceptation
        if self.statut == 'acceptee':
            expedition = self.expedition
            if expedition.statut == 'publiee':  # évite de faire reculer une expédition déjà en cours
                expedition.statut = 'attribuee'
                expedition.save()
            # update() est voulu ici : passer proposee -> refusee n'a aucune règle à valider
            Offre.objects.filter(expedition=expedition, statut='proposee').exclude(pk=self.pk).update(statut='refusee')

    def __str__(self):
        return f"{self.transporteur} → {self.expedition.reference} : {self.prix} DT"