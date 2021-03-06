from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from pip.download import user_agent

from .models import Log, Payement, Utilisateur, EtatPayement
from .forms import PayementViewForm, UtilisateurForm, UtilisateurEditionForm
from ressourcesAdherent.models import Adherent


# Classe qui génère la vue d'affichage des logs avec le template de l'accueil
class ListeLog(ListView):
    #model = Log
    context_object_name = "liste_Log"
    template_name = "accueil.html"
    paginate_by = 20

    # Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeLog, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        filtre = self.request.GET.get('the_search', '')
        if(filtre == ''):
            return Log.objects.all().order_by('-date')
        return Log.objects.filter(Q(editeur__user__username__icontains=filtre)|Q(description__icontains=filtre)).order_by('-date')


# Classe qui génère la vue d'affichage des différents payements.
class ListePayement(ListView):
    #model = Payement
    context_object_name = "liste_Payement"
    template_name = "TPayement.html"
    ordering = ['dateCreation']
    paginate_by = 30

    # Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListePayement, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        filtre = self.request.GET.get('the_search', '')
        if(filtre == ''):
            return Payement.objects.all().order_by('-dateCreation')
        return Payement.objects.filter(Q(beneficiaire__nom__icontains=filtre)|Q(beneficiaire__prenom__icontains=filtre)|
                    Q(rezoman__user__username__icontains=filtre)|Q(banque__icontains=filtre)).order_by('-dateCreation')


# vue pour l'édition d'un payement défini par Id
@login_required
def editerPayement(request, id):
    # On tente de récupérer le payement, et on envoie une page 404 si l'id du payement n'existe pas
    payement = get_object_or_404(Payement, pk=id)

    localId = id  # On sauvegarde l'id en local pour l'envoyer au template
    if request.method == 'POST':  # Si on a reçu la réponse du formulaire
        form = PayementViewForm(request.POST)
        if form.is_valid():  # On vérifie que le formulaire est valide, dans le cas contraire on renvoie la page
            form.editer(Utilisateur.getUtilisateur(request.user), payement)  # On édite le payement
            return redirect('page_payement')  # et on retourne si la page de la liste des payements
    else:
        form = PayementViewForm(
            instance=payement)  # Si c'est le premier appel de cette page, on envoie le formulaire préremplie avec le payement voulu

    # On génère la page ensuite
    return render(request, 'TEditionPayement.html', locals())


# Vue pour la création du payement, très simillaire a la vue précédente
@login_required
def creerPayement(request, adhrId):
    # On récupère les variables locales
    adhr = get_object_or_404(Adherent, pk=adhrId)

    localId = adhrId
    # Si on a reçu un formulaire
    if request.method == 'POST':
        form = PayementViewForm(request.POST)
        if form.is_valid():  # On vérifie s'il est valide
            # Dans ce cas, on crée le payement
            form.instance.beneficiaire = adhr
            form.instance.rezoman = Utilisateur.getUtilisateur(request.user)
            form.save()
            log = Log(editeur=Utilisateur.getUtilisateur(request.user),
                      description="Nouveau payement de {0} euros pour {1}".format(form.instance.credit, form.instance.beneficiaire))
            log.save()
            return redirect('affichageAdherent')  # et on retourne sur la page des adhérent
    else:
        form = PayementViewForm()  # Sinon on envoie un formulaire vide pour créer le payement

    # Et on génère la page
    return render(request, 'TCreationPayement.html', locals())

@login_required
def changerEtatPayement(request, payement_id):
    payement = get_object_or_404(Payement, pk=payement_id)

    if payement.etat == EtatPayement.DECLARE:
        payement.etat = EtatPayement.RECEPTIONNE
        Log.objects.create(editeur=Utilisateur.getUtilisateur(request.user), description="Le Payement de {0} a été receptionné".format(payement.beneficiaire))
    elif payement.etat == EtatPayement.RECEPTIONNE:
        Log.objects.create(editeur=Utilisateur.getUtilisateur(request.user), description="Le Payement de {0} a été encaissé".format(payement.beneficiaire))
        payement.etat = EtatPayement.ENCAISSE

    payement.save()
    return redirect('page_payement')

@login_required
def encaisserCheques(request):
    q1 = Payement.objects.filter(etat=EtatPayement.RECEPTIONNE)
    print(q1)
    for paye in q1:
        if paye.banque != "Liquide":
            paye.etat = EtatPayement.ENCAISSE
            paye.save()
    Log.objects.create(editeur=Utilisateur.getUtilisateur(request.user), description="Encaissement des payement par chèques")
    return redirect('page_payement')

@login_required
def encaisserLiquide(request):
    q1 = Payement.objects.filter(etat=EtatPayement.RECEPTIONNE)
    for paye in q1:
        if paye.banque == "Liquide":
            paye.etat = EtatPayement.ENCAISSE
    Log.objects.create(editeur=Utilisateur.getUtilisateur(request.user), description="Encaissement des payement en liquide")
    return redirect('page_payement')

class ListeUtilisateur(ListView):
    model = Utilisateur
    context_object_name = "liste_utilisateur"
    template_name = "TUtilisateur.html"
    paginate_by = 25

    # Fonction qui sert a demander une session pour accéder au pages de la classe
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ListeUtilisateur, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        filtre = self.request.GET.get('the_search', '')
        if(filtre == ''):
            return Utilisateur.objects.all().order_by('user__username')
        return Utilisateur.objects.filter(Q(user__username__icontains=filtre)).order_by('user__username')

@login_required
def supprimerUtilisateur(request, utilisateur_id):
    utili = get_object_or_404(Utilisateur, pk=utilisateur_id)
    if utili.user.username == "superuser":
        log = Log(editeur=Utilisateur.getUtilisateur(request.user),
                  description="ALERTE : Tentative de suppression du compte superutilisateur malgré les restrictions")
        log.save()
        return redirect('page_accueil')

    for payement in utili.listePayement.all():
        if payement.etat == EtatPayement.DECLARE:
            print("payement en cours, supression impossible")
            return redirect('page_utilisateur')

    utili.user.delete()
    utili.delete()
    return redirect('page_utilisateur')

@login_required
def creer_utilisateur(request):
    if request.user.username != "superuser":
        raise PermissionDenied

    if request.method == 'POST':
        form = UtilisateurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('page_accueil')
    else:
        form = UtilisateurForm()
    return render(request, "TCreationUser.html", locals())

@login_required
def editerUtilisateur(request, userId):
    utili = get_object_or_404(Utilisateur, pk=userId)
    if request.user.username != "superuser" and utili.user != request.user:
        raise PermissionDenied

    form = UtilisateurEditionForm(utili, request.POST)
    if form.is_valid():
        form.editer(Utilisateur.getUtilisateur(request.user))
        return redirect('page_utilisateur')
    return render(request, "TEditionUser.html", locals())
