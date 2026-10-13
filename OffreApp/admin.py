from django.contrib import admin
from .models import Offre


class OffreAdmin(admin.ModelAdmin):
    list_display = ('id', 'prix', 'delai_jours', 'statut', 'expedition', 'transporteur', 'vehicule', 'date_proposition')
    list_filter = ('statut', 'date_proposition')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale', 'vehicule__immatriculation')
    list_editable = ('statut',)



admin.site.register(Offre, OffreAdmin)