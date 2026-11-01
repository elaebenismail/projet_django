from datetime import date

from django.test import TestCase
from django.urls import reverse

from EntrepriseApp.models import Entreprise, Utilisateur

from .models import Expedition


class CloturerExpeditionsTest(TestCase):
    def setUp(self):
        admin = Utilisateur.objects.create_superuser(
            username='admin_test', email='admin.test@gmail.com', password='test-admin-1234')
        gestionnaire = Utilisateur.objects.create_user(
            username='chargeur_test', email='chargeur.test@gmail.com', password='test-chargeur-1234')
        chargeur = Entreprise.objects.create(
            raison_sociale='Chargeur Test', matricule_fiscal='1234567AAM000', type_entreprise='chargeur',
            adresse='12 rue de la Liberté, 1000 Tunis', utilisateur=gestionnaire)

        # Jeu de données varié : statuts mélangés, dont deux « en_cours »
        self.expeditions = []
        for statut in ['publiee', 'attribuee', 'en_cours', 'en_cours', 'livree', 'annulee']:
            self.expeditions.append(Expedition.objects.create(
                ville_depart='Tunis', ville_arrivee='Sfax', poids_kg=500,
                date_souhaitee=date(2026, 12, 1), statut=statut, entreprise=chargeur))
        self.client.force_login(admin)

    def test_seules_les_expeditions_en_cours_sont_cloturees(self):
        response = self.client.post(
            reverse('admin:ExpeditionApp_expedition_changelist'),
            {'action': 'cloturer_expeditions', '_selected_action': [e.pk for e in self.expeditions]},
            follow=True,
        )
        statuts = [Expedition.objects.get(pk=e.pk).statut for e in self.expeditions]
        # Les deux « en_cours » passent à « livree », les autres ne bougent pas
        self.assertEqual(statuts, ['publiee', 'attribuee', 'livree', 'livree', 'livree', 'annulee'])
        self.assertContains(response, "2 expédition(s) clôturée(s), 4 ignorée(s)")