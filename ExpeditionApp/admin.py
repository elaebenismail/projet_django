from django.contrib import admin
from .models import Expedition


class ExpeditionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'ville_depart', 'ville_arrivee', 'poids_kg', 'date_souhaitee', 'statut', 'entreprise')
    list_filter = ('statut', 'date_souhaitee')
    search_fields = ('reference', 'ville_depart', 'ville_arrivee', 'entreprise__raison_sociale')
    list_editable = ('statut',)
    ordering = ('-date_souhaitee',)
    list_per_page = 5
    readonly_fields = ('reference', 'created_at', 'updated_at')
    fieldsets = (
        ('Identification', {
            'fields': ('reference', 'entreprise', 'statut'),
        }),
        ('Trajet', {
            'fields': ('ville_depart', 'ville_arrivee', 'date_souhaitee'),
        }),
        ('Marchandise', {
            'fields': ('poids_kg', 'description'),
        }),
        ('Suivi', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),  # section repliable
        }),
    )


admin.site.register(Expedition, ExpeditionAdmin)