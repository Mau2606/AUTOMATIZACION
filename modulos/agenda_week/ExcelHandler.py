import pandas as pd

class ExcelHandler:
    def __init__(self, ruta_excel):
        self.ruta_excel = ruta_excel
        self.df = self._leer_excel()

    def _leer_excel(self):
        # Leer archivo Excel independientemente de si es .xls o .xlsx
        if self.ruta_excel.endswith('.xls'):
            return pd.read_excel(self.ruta_excel, engine='xlrd')
        else:
            return pd.read_excel(self.ruta_excel)

    def obtener_datos(self):
        # Verificamos que todas las columnas estén en el archivo
        columnas_requeridas = ['FECHA', 'SALA', 'INICIO', 'RIT', 'RUC', 'TIPO DE AUDIENCIA', 'JUEZ', 'CT',
                               'MATERIA']
        if not all(col in self.df.columns for col in columnas_requeridas):
            raise ValueError("El archivo Excel debe contener las columnas: " + ', '.join(columnas_requeridas))
        return self.df[columnas_requeridas]