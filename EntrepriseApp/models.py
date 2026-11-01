from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

matricule_fiscal_validator = RegexValidator(regex=r'^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$', message="format incorrect")


def validate_email(value):
    if not value:
        raise ValidationError("l'adresse email est obligatoire")
    if not value.lower().endswith('@gmail.com'):
        raise ValidationError("format invalid")


class UtilisateurManager(UserManager):
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        return super().create_superuser(username, email, password, **extra_fields)


class Utilisateur(AbstractUser):
    user_id = models.CharField(max_length=8, primary_key=True)
    email = models.EmailField(unique = True, validators=[validate_email])
    telephone = models.CharField(max_length = 15, null=True, blank=True)
    role = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('chargeur', 'Chargeur'),
        ('transporteur', 'Transporteur'),],
        default='chargeur'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UtilisateurManager()

    @classmethod
    def _generate_user_id(cls):  # format AAuserNN, compteur 00-99 remis à zéro chaque année
        annee = timezone.now().strftime('%y')
        prefixe = f"{annee}user"
        dernier = cls.objects.filter(user_id__startswith=prefixe).order_by('-user_id').first()
        compteur = int(dernier.user_id[-2:]) + 1 if dernier else 0
        if compteur > 99:
            raise ValidationError('limit exceeded')
        return f"{prefixe}{compteur:02d}"

    def save(self, *args, **kwargs):
        if not self.user_id:
            self.user_id = self._generate_user_id()
        # Rôle auto-assigné : un superutilisateur a toujours le rôle admin
        if self.is_superuser:
            self.role = 'admin'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user_id} - {self.username}"


class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=255, null=False, blank= False)
    matricule_fiscal = models.CharField(max_length=17, unique=True, validators=[matricule_fiscal_validator])
    type_entreprise = models.CharField(max_length=100, choices=[
        ('chargeur', 'Chargeur'),
        ('transporteur', 'Transporteur')
    ],  default='chargeur')

    adresse = models.TextField(validators=[MinLengthValidator(20, "l'adresse doit au moins avoir 20 char"),MaxLengthValidator(300, "l'adresse ne peut pas depasser les 300 char")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')

    def clean(self):
        # 1234567/A/A/M/000 et 1234567AAM000 deviennent le même matricule (sinon unique=True est contourné)
        if self.matricule_fiscal:
            self.matricule_fiscal = self.matricule_fiscal.upper().replace('/', '').replace('-', '').replace(' ', '')
        # Une entreprise existante ne peut pas changer de type si des objets y sont rattachés
        if self.pk:
            if self.type_entreprise == 'chargeur' and (self.vehicules.exists() or self.offres.exists()):
                raise ValidationError("Cette entreprise a des véhicules ou des offres : elle ne peut pas devenir chargeur.")
            if self.type_entreprise == 'transporteur' and self.expeditions.exists():
                raise ValidationError("Cette entreprise a des expéditions : elle ne peut pas devenir transporteur.")

    def __str__(self):
        return f"{self.raison_sociale} ({self.type_entreprise})"