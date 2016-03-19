# coding=utf8

from django.contrib import admin
from ressourcesAdherent.models import Adherent, Ordinateur


class adminAdherent(admin.ModelAdmin):
    """Classe de gestion d'affichage de l'entité Adhérent"""
    list_display = ('nom', 'prenom', 'dateExpiration', 'estValide')
    list_filter = ('estRezoman', 'estValide')
    date_hierarchy = 'dateExpiration'
    ordering = ('dateExpiration',)
    search_fields = ('nom', 'prenom', 'chambre')
    description = "Adrérent du réseau"
    exclude = ('estValide',)


class adminOrdinateur(admin.ModelAdmin):
    """Classe de gestion d'affichage de l'entité Ordinateur"""
    list_display = ('proprietaire', 'adresseIP', 'adresseMAC')
    list_filter = ('carteWifi',)
    search_fields = ('proprietaire', 'adresseIP', 'adresseMAC')
    description = "Ordinateur autorisé"
    exclude = ('nomDNS', 'adresseIP')


admin.site.register(Adherent, adminAdherent)  # Link de l'entité Adhérent
admin.site.register(Ordinateur, adminOrdinateur)  # Link de l'entité Ordinateur
