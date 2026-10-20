from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html
from .models import Expedition
from OffreApp.models import Offre


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


class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fk_name = 'expedition'
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    show_change_link = True
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False  # lecture seule : on ne dépose pas d'offre depuis la fiche expédition


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    inlines = [OffreInline]
    autocomplete_fields = ('entreprise',)
    list_display = ('reference', 'entreprise', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut', 'statut_colore')
    list_filter = ('statut', 'ville_depart', EnRetardFilter)
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_souhaitee'
    list_per_page = 25
    readonly_fields = ('reference', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations', {'fields': ('reference', 'entreprise', 'statut', 'ville_depart', 'ville_arrivee', 'poids_kg', 'description')}),
        ('Dates', {'fields': ('date_souhaitee', 'created_at', 'updated_at')}),
    )
    actions = ['cloturer_expeditions']

    @admin.display(description='État')
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
                self.message_user(request, f"{expedition.reference} : {e}", messages.ERROR)
        self.message_user(request, f"{cloturees} expédition(s) clôturée(s), {ignorees} ignorée(s) (pas « en cours »), {erreurs} en erreur.", messages.SUCCESS)