"""
Tworzy otwarte dokumentu FV z dokumentów WZ.
"""
import datetime


class GeneratorFV:


    @staticmethod
    def last_day_of_month(date_1, date_2):
        """
        Zwraca True jeżeli podane daty różnią się miesiącami.
        """
        if isinstance(date_1, datetime.date) and isinstance(date_2, datetime.date): 
            return date_1.month == date_2.month
        else:
            raise AttributeError("Argument musi być typu datetime!")
