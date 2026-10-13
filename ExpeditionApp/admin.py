from django.contrib import admin
from .models import Expedition


class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut', 'entreprise')
    list_filter = ('statut', 'date_souhaitee')
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    list_editable = ('statut',)


admin.site.register(Expedition, ExpeditionAdmin)