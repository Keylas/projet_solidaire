##Liste des urls liée au module ressourcesAdhérent avec les vues associées

from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views
from . import views

##Liste des patterns des urls sous la forme (regex, views, nom_relatif)
urlpatterns = [
    url(r'^listeAdherent$', views.ListeAdherent.as_view(), name="affichageAdherent"), # page pour afficher les adherents
    url(r'^rezotage$', views.rezotage, name="pageRezotage"), # page de rezotage d'un nouvel adherent
    url(r'^listeOrdinateur$', views.ListeOrdinateur.as_view(), name="affichageOrdinateur"), # page pour afficher les ordinateurs
    url(r'^editionA/(?P<adhrId>[0-9]+)$', views.editionA, name="editionAdherent"),
    url(r'^supprimerOrdi/(?P<ordiPk>[A-Za-z1-9]+)$', views.supressionOrdinateur, name="suppressionO")
]
