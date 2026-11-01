import csv
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.html import format_html
from .models import Offre


@admin.action(description="Exporter la sélection en CSV")
def exporter_offres_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="offres.csv"'
    writer = csv.writer(response)
    writer.writerow(['reference_expedition', 'transporteur', 'prix', 'statut'])
    # select_related() : expédition et transporteur chargés en une seule requête SQL
    for offre in queryset.select_related('expedition', 'transporteur'):
        writer.writerow([offre.expedition.reference, offre.transporteur.raison_sociale, offre.prix, offre.statut])
    return response


@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    autocomplete_fields = ('expedition', 'transporteur', 'vehicule')
    list_display = ('id', 'expedition', 'transporteur', 'vehicule', 'prix', 'delai_jours', 'date_proposition', 'statut_colore', 'statut')
    list_filter = ('statut', 'transporteur', 'date_proposition')
    search_fields = ('expedition__reference', 'transporteur__raison_sociale', 'vehicule__immatriculation')
    # Seul le statut est modifiable depuis la liste : prix et délai restent protégés
    list_editable = ('statut',)
    ordering = ('-created_at',)
    date_hierarchy = 'date_proposition'
    list_per_page = 25
    actions = [exporter_offres_csv]
    readonly_fields = ('statut_colore', 'date_proposition', 'created_at', 'updated_at')
    fieldsets = (
        ("Détails de l'offre", {'fields': ('expedition', 'transporteur', 'vehicule')}),
        ('Conditions', {'fields': ('prix', 'delai_jours')}),
        ('Suivi', {'fields': ('statut', 'statut_colore', 'date_proposition', 'created_at', 'updated_at')}),
    )

    # Une offre acceptée ne peut plus changer de prix ni de délai
    def get_readonly_fields(self, request, obj=None):
        base = list(self.readonly_fields)
        if obj and obj.statut == 'acceptee':
            return base + ['prix', 'delai_jours']
        return base

    # Si l'enregistrement viole une règle métier (ex : 2 offres acceptées d'un coup
    # depuis la liste), on affiche un message au lieu d'une page d'erreur 500
    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError as e:
            self.message_user(request, f"Offre « {obj} » non enregistrée : {' '.join(e.messages)}", level=messages.ERROR)

    @admin.display(description='État', ordering='statut')
    def statut_colore(self, obj):
        couleurs = {'proposee': '#F0AD4E', 'acceptee': '#5CB85C', 'refusee': '#D9534F', 'retiree': '#777777'}
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, '#999'), obj.get_statut_display(),
        )