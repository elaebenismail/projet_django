from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Entreprise, Utilisateur
from VehiculeApp.models import Vehicule

admin.site.site_header = 'TransConnect - Administration'
admin.site.site_title = 'TransConnect'
admin.site.index_title = "Tableau de bord"


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('user_id', 'username', 'email', 'role', 'telephone', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user_id', 'username', 'email', 'telephone')
    list_editable = ('role', 'telephone')
    ordering = ('user_id',)
    readonly_fields = ('user_id', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('user_id', 'username', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'telephone')}),
        ('Rôle et permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Horodatage', {'fields': ('date_joined', 'last_login', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    # Formulaire de création : pas de user_id ni d'historique, mais password1/password2
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('username', 'usable_password', 'password1', 'password2', 'email', 'telephone', 'role')}),
    )


class VehiculeInline(admin.TabularInline):
    model = Vehicule
    fields = ('immatriculation', 'type_vehicule', 'capacite_kg', 'disponible')
    extra = 1
    show_change_link = True


@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    inlines = [VehiculeInline]
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