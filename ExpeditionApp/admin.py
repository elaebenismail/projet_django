from django.contrib import admin
from django.utils import timezone
from .models import Expedition


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


@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    autocomplete_fields = ('entreprise',)
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut', 'entreprise')
    list_filter = ('statut', 'date_souhaitee', EnRetardFilter)
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    list_editable = ('statut',)
    ordering = ('-date_souhaitee',)
    list_per_page = 10
    readonly_fields = ('reference', 'created_at', 'updated_at')
    fieldsets = (
        ('Informations',
          {'fields': ('reference', 'entreprise', 'statut', 'ville_depart', 'ville_arrivee', 'poids_kg', 'description')}),
        ('Dates', 
         {'fields': ('date_souhaitee', 'created_at', 'updated_at')}),
    )