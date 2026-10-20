from django.contrib import admin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Entreprise


class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('raison_sociale', 'matricule_fiscal', 'type_entreprise', 'utilisateur', 'created_at')
    list_filter = ('type_entreprise', 'created_at')
    search_fields = ('raison_sociale', 'matricule_fiscal', 'utilisateur__username', 'utilisateur__email')
    list_select_related = ('utilisateur',)
    list_editable = ('type_entreprise',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ("Identité de l'entreprise", {'fields': ('raison_sociale', 'matricule_fiscal', 'type_entreprise')}),
        ('Contact et gestion', {'fields': ('adresse', 'utilisateur')}),
        ('Horodatage', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


class UtilisateurAdmin(UserAdmin):
    list_display = ('user_id', 'email', 'role', 'telephone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user_id', 'email', 'telephone')
    list_editable = ('role', 'telephone')
    ordering = ('user_id',)
    readonly_fields = ('user_id', 'created_at', 'updated_at')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations TransConnect', {'fields': ('user_id', 'role', 'telephone')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {'fields': ('email', 'role', 'telephone')}),)


admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Entreprise, EntrepriseAdmin)