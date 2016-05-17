from ressourcesAdherent.models import Adherent
from django.utils.timezone import datetime
import threading

class Donnee:
    dateCoupure = None
    listeCoupure = []
    mutex = threading.Lock()
    timer = None

def executerCoupure():
    Donnee.mutex.acquire()
    for adhrId in Donnee.listeCoupure:
        try:
            adhr = Adherent.objects.get(pk=adhrId)
            if adhr.dateExpiration - datetime.now() < 0:
                adhr.estValide = False
                adhr.save()
        except Adherent.DoesNotExist:
            pass
    Donnee.mutex.release()
    initialiserListe()

def setTimer():
    tps = Donnee.dateCoupure - datetime.now()
    Donnee.timer = threading.Timer(tps.seconds, executerCoupure)


def initialiserListe():
    Donnee.listeCoupure = []
    Donnee.mutex.acquire()
    q1 = Adherent.objects.all().order_by('dateExpiration')
    Donnee.dateCoupure = q1[0].dateExpiration
    q1 = q1.filter(dateExpiration=Donnee.dateCoupure)
    for adhr in q1:
        Donnee.listeCoupure.append(adhr.pk)
    setTimer()
    Donnee.mutex.release()

def modifAdherent(adhrId):
    try:
        adhr = Adherent.objects.get(pk=adhrId)
        Donnee.mutex.acquire()
        if adhr.dateExpiration == Donnee.dateCoupure:
            Donnee.listeCoupure.append(adhrId)
        elif adhr.dateExpiration < Donnee.dateCoupure:
            Donnee.listeCoupure = [adhrId]
            Donnee.dateCoupure = adhr.dateExpiration
            setTimer()
        Donnee.mutex.release()
    except Adherent.DoesNotExist:
        pass

