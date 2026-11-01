from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html
from .models import Expedition
from OffreApp.models import Offre


# Filtre calculé : expéditions encore publiées alors que la date souhaitée est dépassée
class EnRetardFilter(admin.SimpleListFilter):
    title = "en retard"
    parameter_name = "en_retard"

    def lookups(self, request, model_admin):
        return [("oui", "Oui"), ("non", "Non")]

    def queryset(self, request, queryset):
        aujourd_hui = timezone.now().date()
        if self.value() == "oui":
            return queryset.filter(statut="publiee", date_souhaitee__lt=aujourd_hui)
        if self.value() == "non":
            return queryset.exclude(statut="publiee", date_souhaitee__lt=aujourd_hui)
        return queryset


# Offres reçues, consultables depuis la fiche de l'expédition sans pouvoir les modifier
class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fk_name = 'expedition'
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    show_change_link = True
    can_delete = False

    # Une offre est déposée par un transporteur : pas d'ajout depuis la fiche expédition
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    inlines = [OffreInline]
    autocomplete_fields = ('entreprise',)
    list_display = ('reference', 'entreprise', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut', 'statut_colore')
    list_filter = ('statut', 'ville_depart', EnRetardFilter)
    # Obligatoire pour l'autocomplete_fields 'expedition' de OffreAdmin
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25
    # statut_colore est une méthode : elle doit être en lecture seule pour apparaître dans fieldsets
    readonly_fields = ('reference', 'statut_colore', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations', {'fields': ('reference', 'entreprise', 'statut', 'statut_colore', 'ville_depart', 'ville_arrivee', 'poids_kg', 'description')}),
        ('Dates', {'fields': ('date_souhaitee', 'created_at', 'updated_at')}),
    )
    actions = ['cloturer_expeditions']

    @admin.display(description='État', ordering='statut')
    def statut_colore(self, obj):
        couleurs = {
            'publiee': '#F0AD4E', 'attribuee': '#337AB7', 'en_cours': '#8E5EA2',
            'livree': '#5CB85C', 'annulee': '#D9534F',
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, '#999'), obj.get_statut_display(),
        )

    @admin.action(description="Clôturer les expéditions sélectionnées")
    def cloturer_expeditions(self, request, queryset):
        cloturees, ignorees, erreurs = 0, 0, 0
        # Boucle + full_clean() + save() plutôt que .update() : les règles métier s'exécutent
        for expedition in queryset:
            if expedition.statut != 'en_cours':
                ignorees += 1
                continue
            expedition.statut = 'livree'
            try:
                expedition.full_clean()
                expedition.save()
                cloturees += 1
            except ValidationError as e:
                erreurs += 1
                self.message_user(request, f"{expedition.reference} : {' '.join(e.messages)}", messages.ERROR)
        self.message_user(request, f"{cloturees} expédition(s) clôturée(s), {ignorees} ignorée(s) (pas « en cours »), {erreurs} en erreur.", messages.SUCCESS)