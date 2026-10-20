from django.contrib import admin
from .models import Offre


class OffreAdmin(admin.ModelAdmin):
    list_display = ('id', 'prix', 'delai_jours', 'statut', 'expedition', 'transporteur', 'vehicule', 'date_proposition')
    list_filter = ('statut', 'date_proposition')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale', 'vehicule__immatriculation')
    list_editable = ('statut',)
    readonly_fields = ('date_proposition', 'created_at', 'updated_at')

    fieldsets = (
        ('Informations', {
            'fields': ('expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'statut'),
        }),
        ('Dates', {
            'fields': ('date_proposition', 'created_at', 'updated_at'),
        }),
    )


admin.site.register(Offre, OffreAdmin)