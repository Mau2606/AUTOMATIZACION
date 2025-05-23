
import os, re

class CarpetaYArchivoManager:
    def __init__(self, ruta_base, tipo_semana):
        self.tipo_semana = tipo_semana
        self.ruta_base = ruta_base
        self.correlativo = 1
        self.fecha_actual = ''

    def crear_carpeta_y_archivo(self, fecha, rit, sala, juez, tipo_audiencia, word_handler, materia):
        ruta_carpeta = os.path.join(self.ruta_base, f'{fecha} - SALA {sala} - {self.tipo_semana} - {self._abrevia_juez(juez)}')
        os.makedirs(ruta_carpeta, exist_ok=True)

        if fecha != self.fecha_actual:
            self.fecha_actual = fecha
            self.correlativo = 1

        ruta_archivo = os.path.join(ruta_carpeta, f'{ ("" if self.correlativo>=10 else "0")}{self.correlativo}. {rit} - {self._abrevia_tipo_audiencia(tipo_audiencia)} - {self._abreviar_materia(materia) +" -" if rit[0]=="C" else ""}.docx')
        self.correlativo += 1
        word_handler.copiar_y_renombrar(ruta_archivo)

        print(f'Carpeta creada y archivo Word copiado: {ruta_archivo}')
        return ruta_archivo

    def _abrevia_juez(self, juez):
        juez = juez.split(' ')
        abreviacion = ''
        for i in range(len(juez)):
             abreviacion = abreviacion + juez[i][0]
        return abreviacion

    def _abrevia_tipo_audiencia(self, tipo_audiencia):
        if tipo_audiencia == 'PREPARATORIA':
            return 'AP'
        elif tipo_audiencia == 'JUICIO':
            return 'AJ'
        elif tipo_audiencia == 'REVISION':
            return 'AR'
        else:
            return 'AE'

    def _abreviar_materia(self, materia):
        # Tabla de abreviaciones
        abreviaciones = {
            'Alimentos': 'ALI',
            'Alimentos, Cesacion': 'ALI CESE',
            'Alimentos, Rebaja': 'ALI REB',
            'Alimentos, Aumento': 'ALI AUM',
            'Compensacion Economica': 'COMP. ECON.',
            'Cuidado Personal Del Niño': 'C.P.',
            'Cuidado Personal Del Niño, Declaracion': 'C.P.',
            'Cuidado Personal Del Niño, Modificacion': 'C.P.',
            'Divorcio De Comun Acuerdo': 'DIV C. A.',
            'Divorcio Por Cese De Convivencia': 'DIV',
            'Divorcio Por Culpa': 'DIV CULPA',
            'Paternidad, Impugnacion Y Reconocimiento De': 'PATERNIDAD IMPUG Y RECO',
            'Paternidad, Reconocimiento De': 'PATERNIDAD RECO',
            'Relacion Directa Y Regular Con El Niño': 'RDR',
            'Relacion Directa Y Regular Modificacion': 'RDR MODIF',
            'Relación Directa Y Regular Suspensión': 'RDR SUSP:',
            'Autorizacion Salida Del Pais': 'AUTOR. SAL PAIS',
            'Otros Asuntos De Tramitacion Ordinaria': 'OTROS ASUNTOS',
            'Adopcion': 'ADOPCION',
            'Separacion Judicial De Bienes': 'SEP. JUD. DE BIENES',
            'Declaracion De Bienes Familiares': 'DECL. BIEN FAM'



        }

        # Paso 1: Quitar los números y crear una lista de materias
        materias = [m.strip() for m in re.split(r'\d+\.', materia) if m.strip()]

        # Paso 2: Abreviar cada materia según la tabla
        abreviadas = []
        for mat in materias:
            abreviacion = abreviaciones.get(mat)  # Si no encuentra la abreviación, deja el nombre original
            abreviadas.append(abreviacion)

        # Paso 3: Unir las abreviaciones con un "I" si es necesario
        resultado = ' I '.join(abreviadas)

        return resultado