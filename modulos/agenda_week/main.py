import os, re
from datetime import datetime

from modulos.agenda_week.ExcelHandler import ExcelHandler
from modulos.agenda_week.WordHandler import WordHandler
from modulos.agenda_week.folder_and_file_manager import CarpetaYArchivoManager
from modulos.agenda_week.tools_class import FechaEnPalabras, PlantillaSelector


class GestorPrincipal:
    def __init__(self, ruta_excel, ruta_plantillas, ruta_base, tipo_semana):
        self.excel_handler = ExcelHandler(ruta_excel)
        self.ruta_plantillas = ruta_plantillas
        self.carpeta_archivo_manager = CarpetaYArchivoManager(ruta_base, tipo_semana)

    def procesar(self):
        # Obtener datos con las columnas actualizadas
        datos = self.excel_handler.obtener_datos()

        for _, row in datos.iterrows():
            fecha = datetime.strptime(row['FECHA'], '%d/%m/%Y')
            sala = str(row['SALA'])
            inicio = row['INICIO']  # Hora de inicio
            rit = str(row['RIT'])
            ruc = str(row['RUC'])
            tipo_audiencia = row['TIPO DE AUDIENCIA']
            juez = row['JUEZ']
            ct = row['CT']
            materia = row['MATERIA']

            # Convertir la fecha a palabras
            fecha_palabras = FechaEnPalabras(fecha).convertir()

            # Manejo del archivo Word
            word_handler = WordHandler(os.path.join(self.ruta_plantillas, PlantillaSelector(rit[0]).seleccionar_plantilla()))

            # Crear carpeta y rellenar el archivo Word
            ruta_archivo = self.carpeta_archivo_manager.crear_carpeta_y_archivo(fecha.strftime('%Y-%m-%d'), rit, sala, juez, tipo_audiencia, word_handler, materia)

            # Rellenar los demás campos en el archivo Word, incluyendo la hora de inicio
            word_handler.rellenar_datos_completos(
                ruta_word=ruta_archivo,
                #titulo=ToolFuction.crear_titulo(tipo_audiencia,materia),
                titulo=self.crear_titulo(tipo_audiencia,materia),
                fecha_en_palabras=fecha_palabras,
                ruc=ruc,
                rit=rit,
                juez=juez,
                ct=ct,
                audio=self.formatear_ruc(ruc),
                sala=sala,
                inicio=inicio
            )


    def crear_titulo(self, tipo_audiencia, materia):
        titulo = "ACTA DE AUDIENCIA "
        materias = [m.strip() for m in re.split(r'\d+\.', materia) if m.strip()]
        traducion = {
            'Alimentos': 'ALIMENTOS',
            'Alimentos, Cesacion': 'CESE DE ALIMENTOS',
            'Alimentos, Rebaja': 'REBAJA DE ALIMENTOS',
            'Alimentos, Aumento': 'AUMENTO DE ALIMENTOS',
            'Compensacion Economica': 'COMPENSACIÓN ECONÓMICA',
            'Cuidado Personal Del Niño': 'CUIDADO PERSONAL',
            'Cuidado Personal Del Niño, Declaracion': 'DECLARACION DE CUIDADO PERSONAL',
            'Cuidado Personal Del Niño, Modificacion': 'MODIFICACION DE CUIDADO PERSONAL',
            'Divorcio De Comun Acuerdo': 'DIVORCIO DE COMÚN ACUERDO',
            'Divorcio Por Cese De Convivencia': 'DIVORCIO',
            'Divorcio Por Culpa': 'DIVORCIO POR CULPA',
            'Paternidad, Impugnacion Y Reconocimiento De': 'IMPUGNACIÓN Y RECONOCIMIENTO DE PATERNIDAD',
            'Paternidad, Reconocimiento De': 'RECONOCIMIENTO DE PATERNIDAD',
            'Relacion Directa Y Regular Con El Niño': 'RELACIÓN DIRECTA Y REGULAR',
            'Relacion Directa Y Regular Modificacion': 'MODIFICACIÓN DE RELACIÓN DIRECTA Y REGULAR',
            'Relacion Directa Y Regular Suspensión': 'SUSPENSIÓN DE RELACIÓN DIRECTA Y REGULAR:',
            'Violencia Intrafamiliar': 'VIOLENCIA INTRAFAMILIAR',
            'Violencia de Género': 'VIOLENCIA INTRAFAMILIAR',
            'Vulneración De Derechos': 'MEDIDA DE PROTECCION',
            'Autorizacion Salida Del Pais':'AUTORIZACIÓN DE SALIDA DEL PAÍS',
            'Declaracion De Susceptibilidad': 'SUSCEPTIBILIDAD DE ADOPCIÓN',
            'Otros Procedimientos Menores': 'REVISIÓN DE MEDIDA DE PROTECCION',
            'Adopcion': 'ADOPCIÓN',
            'Separacion Judicial De Bienes': 'SEPARACIÓN JUDICIAL DE BIENES',
            'Declaracion De Bienes Familiares': 'DECLARACIÓN DE BIEN FAMILIAR'

        }
        materias_array = []
        for mat in materias:
            mate = traducion.get(mat, mat)  # Si no encuentra la abreviación, deja el nombre original
            materias_array.append(mate)
        resultado = ', '.join(materias_array)
        if tipo_audiencia == 'PREPARATORIA':
            titulo += "PREPARATORIA"
        elif tipo_audiencia == 'JUICIO':
            titulo += "DE JUICIO"
        elif tipo_audiencia == 'REVISION':
            titulo += "DE REVISION"
        else:
            titulo += "ESPECIAL"
        return f"{titulo} DE {resultado}"

    def formatear_ruc(self, ruc):
        # Paso 1: Eliminar los espacios en blanco
        ruc_limpio = ruc.replace(" ", "").replace("-", "", 2)
        return f"{ruc_limpio}-1651"

# Ejecución del script
if __name__ == "__main__":
    # Especifica las rutas
    ruta_excel = 'audiencias.xls'  # Puede ser .xls o .xlsx
    ruta_word_plantilla = os.path.join(os.getcwd(), 'plantillas')  # Puede ser .doc o .docx
    ruta_base = os.path.join(os.getcwd(), 'salida')  # Carpeta donde se creará la estructura
    tipo_semana = 'CONT'

    gestor = GestorPrincipal(ruta_excel, ruta_word_plantilla, ruta_base, tipo_semana)
    gestor.procesar()