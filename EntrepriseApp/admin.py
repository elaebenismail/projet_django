from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Entreprise


class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'utilisateur', 'created_at')
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_sociale', 'matricule_fiscal')
    list_editable = ('type_entreprise',)



class UtilisateurAdmin(UserAdmin):
    list_display = ('user_id', 'email', 'role', 'telephone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user_id', 'email', 'telephone')
    list_editable = ('role', 'telephone')

admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Entreprise, EntrepriseAdmin)