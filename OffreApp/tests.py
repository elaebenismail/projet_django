from django.test import TestCase
from django.core.exceptions import ValidationError

from EntrepriseApp.models import Utilisateur, Entreprise
from VehiculeApp.models import Vehicule
from ExpeditionApp.models import Expedition
from OffreApp.models import Offre


class TransConnectTests(TestCase):
    def setUp(self):
        u1 = Utilisateur.objects.create_user(username='a', email='a@gmail.com', password='x')
        u2 = Utilisateur.objects.create_user(username='b', email='b@gmail.com', password='x')
        u3 = Utilisateur.objects.create_user(username='c', email='c@gmail.com', password='x')
        adresse = 'Adresse de plus de vingt caracteres'
        self.chargeur = Entreprise.objects.create(
            raison_sociale='Charg', matricule_fiscal='1234567AAM000',
            type_entreprise='chargeur', adresse=adresse, utilisateur=u1)
        self.transp = Entreprise.objects.create(
            raison_sociale='Transp', matricule_fiscal='7654321BAM000',
            type_entreprise='transporteur', adresse=adresse, utilisateur=u2)
        self.transp2 = Entreprise.objects.create(
            raison_sociale='Transp2', matricule_fiscal='1111111CAM000',
            type_entreprise='transporteur', adresse=adresse, utilisateur=u3)
        self.vehicule = Vehicule.objects.create(
            immatriculation='123TUN4567', capacite_kg=3500, type_vehicule='fourgon', entreprise=self.transp)
        self.vehicule2 = Vehicule.objects.create(
            immatriculation='999TUN0001', capacite_kg=3500, type_vehicule='fourgon', entreprise=self.transp2)
        self.exp = Expedition.objects.create(
            ville_depart='Tunis', ville_arrivee='Sfax', poids_kg=1000,
            date_souhaitee='2026-11-01', entreprise=self.chargeur)

    def offre(self, **kw):
        data = dict(prix=500, delai_jours=2, expedition=self.exp,
                    transporteur=self.transp, vehicule=self.vehicule)
        data.update(kw)
        return Offre.objects.create(**data)

    # --- Utilisateur / Entreprise / Expedition ---
    def test_user_id_format(self):
        self.assertRegex(Utilisateur.objects.get(username='a').user_id, r'^\d{2}user\d{2}$')

    def test_email_doit_etre_gmail(self):
        with self.assertRaises(ValidationError):
            Utilisateur(username='z', email='z@yahoo.com').full_clean()

    def test_matricule_invalide(self):
        e = Entreprise(raison_sociale='X', matricule_fiscal='abc', type_entreprise='chargeur',
                       adresse='Adresse de plus de vingt caracteres', utilisateur=self.chargeur.utilisateur)
        with self.assertRaises(ValidationError):
            e.full_clean()

    def test_reference_expedition(self):
        self.assertRegex(self.exp.reference, r'^EXP-\d{2}-\d{5}$')

    def test_poids_nul_refuse(self):
        with self.assertRaises(ValidationError):
            Expedition.objects.create(ville_depart='A', ville_arrivee='B', poids_kg=0,
                                      date_souhaitee='2026-11-01', entreprise=self.chargeur)

    def test_expedition_par_transporteur_refusee(self):
        with self.assertRaises(ValidationError):
            Expedition.objects.create(ville_depart='A', ville_arrivee='B', poids_kg=10,
                                      date_souhaitee='2026-11-01', entreprise=self.transp)

    # --- Vehicule ---
    def test_vehicule_capacite_nulle(self):
        with self.assertRaises(ValidationError):
            Vehicule.objects.create(immatriculation='000TUN0000', capacite_kg=0,
                                    type_vehicule='fourgon', entreprise=self.transp)

    def test_vehicule_pour_chargeur_refuse(self):
        with self.assertRaises(ValidationError):
            Vehicule.objects.create(immatriculation='000TUN0001', capacite_kg=100,
                                    type_vehicule='fourgon', entreprise=self.chargeur)

    def test_vehicule_capacite_superieure_au_max_du_type(self):
        with self.assertRaises(ValidationError):
            Vehicule.objects.create(immatriculation='000TUN0002', capacite_kg=2000,
                                    type_vehicule='camionnette', entreprise=self.transp)

    # --- Règles métier Offre ---
    def test_regle1_offre_par_chargeur(self):
        with self.assertRaises(ValidationError):
            self.offre(transporteur=self.chargeur)

    def test_regle2_vehicule_autre_entreprise(self):
        with self.assertRaises(ValidationError):
            self.offre(vehicule=self.vehicule2)

    def test_regle3_expedition_non_publiee(self):
        self.exp.statut = 'livree'
        self.exp.save()
        with self.assertRaises(ValidationError):
            self.offre()

    def test_regle4_doublon_proposee(self):
        self.offre()
        with self.assertRaises(ValidationError):
            self.offre()

    def test_regle5_cascade_acceptation(self):
        o1 = self.offre()
        o2 = self.offre(transporteur=self.transp2, vehicule=self.vehicule2)
        o1.statut = 'acceptee'
        o1.save()
        self.exp.refresh_from_db()
        o2.refresh_from_db()
        self.assertEqual(self.exp.statut, 'attribuee')
        self.assertEqual(o2.statut, 'refusee')

    def test_cascade_ne_fait_pas_reculer_une_expedition_en_cours(self):
        o1 = self.offre()
        self.exp.statut = 'en_cours'
        self.exp.save()
        o1.statut = 'acceptee'
        o1.save()
        self.exp.refresh_from_db()
        self.assertEqual(self.exp.statut, 'en_cours')

    def test_une_seule_offre_acceptee_par_expedition(self):
        o1 = self.offre()
        o2 = self.offre(transporteur=self.transp2, vehicule=self.vehicule2)
        o1.statut = 'acceptee'
        o1.save()
        o2.refresh_from_db()  # o2 est passée à « refusee »
        o2.statut = 'acceptee'
        with self.assertRaises(ValidationError):
            o2.save()

    def test_regle6_vehicule_indisponible(self):
        self.vehicule.disponible = False
        self.vehicule.save()
        with self.assertRaises(ValidationError):
            self.offre()

    def test_regle7_poids_superieur_au_max_du_type(self):
        petit = Vehicule.objects.create(immatriculation='111TUN0001', capacite_kg=1500,
                                        type_vehicule='camionnette', entreprise=self.transp)
        self.exp.poids_kg = 3000
        self.exp.save()
        with self.assertRaises(ValidationError):
            self.offre(vehicule=petit)  # camionnette limitée à 1500 kg

    def test_regle7_camion_porteur_pour_petit_poids(self):
        camion = Vehicule.objects.create(immatriculation='222TUN0001', capacite_kg=19000,
                                         type_vehicule='camion_porteur', entreprise=self.transp)
        with self.assertRaises(ValidationError):
            self.offre(vehicule=camion)  # expédition de 1000 kg : trop léger pour un porteur

    def test_prix_et_delai(self):
        with self.assertRaises(ValidationError):
            self.offre(prix=0)
        with self.assertRaises(ValidationError):
            self.offre(delai_jours=0)