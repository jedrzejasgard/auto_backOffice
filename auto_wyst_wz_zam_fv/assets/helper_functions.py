import datetime

def today():
    """
    Zwraca dzisiejszą datę w formacie RRRR-MM-DD
    """
    a = datetime.date.today()
    b = a + datetime.timedelta(-3)
    return b.strftime('%Y-%m-%d')


def ostatni_dzien_miesiaca(data_dzis):
    """
    Jeżeli jutro miesiąc będzie inny niż dziś to funkcja zwróci True.

    data_dzis -> typ datetime
    """
    jutro = data_dzis + datetime.timedelta(1)
    return jutro.month != data_dzis.month


def hour_threshold(now, threshold):
    """
    Zwraca True jeżeli aktualna godzina jest większa
    niz podany parametr.
    
    now -> typu datetime
    threshold - typu int
    """
    if 0 > threshold or threshold > 24:
        raise AttributeError('Podana godzina musi zawierać się między 1 a 12')
    if not isinstance(now, (datetime.time, datetime.datetime)):
        raise TypeError('now musi być typu datetime')
    if not isinstance(threshold, int):
        raise TypeError('threshold musi być typu int')
        
    return now.hour >= threshold


def mozna_fakturowac_otwarte_wz(odm, ht):
    aktualna_godzina = datetime.datetime.now()
    return ostatni_dzien_miesiaca(odm) and hour_threshold(aktualna_godzina, ht)
