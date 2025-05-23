from datetime import datetime
from num2words import num2words
import re


# Clase para manejar la traducción de fechas
class FechaEnPalabras:
    def __init__(self, fecha):
        self.fecha = fecha

    def convertir_fecha(self, fecha):
        # Convertimos la fecha de string a datetime usando el formato dado
        fecha_convertida = datetime.strptime(fecha, "%d/%m/%Y")
        # Convertimos la fecha al formato deseado
        return fecha_convertida.strftime("%Y-%m-%d")

    def _mes_en_palabras(self, mes):
        meses = {
            1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
            7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
        }
        return meses.get(mes, "mes desconocido")

    def convertir(self):

        dia = num2words(self.fecha.day, lang='es')
        mes = self._mes_en_palabras(self.fecha.month)
        anio = num2words(self.fecha.year, lang='es')
        return f"{dia} de {mes} de {anio}"


# Clase para manejar la selección automática de plantillas
class PlantillaSelector:
    def __init__(self, letra_rit):
        self.letra_rit = letra_rit.upper()

    def seleccionar_plantilla(self):
        # Aquí puedes agregar más plantillas según otras letras
        if self.letra_rit == 'F':
            return 'plantilla_F.docx'
        elif self.letra_rit == 'P' or self.letra_rit == 'X' or self.letra_rit == 'A':
            return 'plantilla_P.docx'
        elif self.letra_rit == 'C':
            return 'plantilla_C.docx'
        else:
            return 'plantilla_generica.docx'
