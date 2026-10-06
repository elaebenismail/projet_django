from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError 

matricule_fiscal_validator = RegexValidator(regex='^\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$', message="format incorrect")

def validate_email(value):
    if not value:
        raise ValidationError("l'adresse email est obligatoire")
    if not value.endswith('@gmail.com'):
        raise ValidationError("format invalid")

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


class Entreprise(models.Model):
    raison_sociale = models.CharField(max_length=255, null=False, blank= False)
    matricule_fiscale = models.CharField(max_length=17, unique=True, validators=[matricule_fiscal_validator])
    type_entreprise = models.CharField(max_length=100, choices=[
        ('chargeur', 'Chargeur'),
        ('transporteur', 'Transporteur')
    ],  default='chargeur')

    adresse = models.TextField(validators=[MinLengthValidator(20, "l'adresse doit au moins avoir 20 char"),MaxLengthValidator(300, "l'adresse ne peut pas depasser les 300 char")])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    gerant = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='entreprise')


