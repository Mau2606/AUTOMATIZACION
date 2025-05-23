import re

class Registro:
    def __init__(self, sujeto, nombre, rut, direccion, email, telefono, estado, fecha_nacimiento=None, edad=None):
        self.sujeto = sujeto
        self.nombre = nombre
        self.rut = rut
        self.direccion = direccion
        self.email = email
        self.telefono = telefono
        self.estado = estado
        self.fecha_nacimiento = fecha_nacimiento
        self.edad = edad

    def __repr__(self):
        return (f"Sujeto: {self.sujeto}, Nombre o Razón Social: {self.nombre}, "
                f"Rut/Pasaporte: {self.rut}, Dirección: {self.direccion}, "
                f"Email: {self.email}, Teléfono: {self.telefono}, "
                f"Estado: {self.estado}, Fecha de nacimiento: {self.fecha_nacimiento}, "
                f"Edad: {self.edad}")


class ExtractorDeRegistros:
    def __init__(self, texto):
        self.texto = texto
        self.registros = []

    def extraer_datos(self):
        # Dividimos el texto en bloques usando un patrón que busca 'Confirmado', 'Pendiente' o 'Eliminado'
        bloques = re.split(r"(?:Confirmado|Pendiente|Eliminado)", self.texto)

        # Iteramos sobre cada bloque y extraemos los datos
        for bloque in bloques:
            if bloque.strip():  # Verificamos que el bloque no esté vacío
                sujeto = self._extraer_sujeto(bloque)
                estado = self._extraer_estado(bloque)
                rut = self._extraer_rut(bloque)
                nombre = self._extraer_nombre(bloque)
                direccion = self._extraer_direccion(bloque)
                email = self._extraer_email(bloque)
                telefono = self._extraer_telefono(bloque)
                fecha_nacimiento, edad = self._extraer_fecha_nacimiento(bloque, sujeto)

                registro = Registro(sujeto, nombre, rut, direccion, email, telefono, estado, fecha_nacimiento, edad)
                self.registros.append(registro)

    def _extraer_sujeto(self, bloque):
        match = re.search(r"^([^\d]+)", bloque)
        return  match.group(1).strip() if match else "Desconocido"

    def _extraer_estado(self, bloque):
        # Extrae el estado del bloque: Confirmado, Pendiente o Eliminado
        if "Confirmado" in bloque:
            return "Confirmado"
        elif "Pendiente" in bloque:
            return "Pendiente de pronunciación"
        elif "Eliminado" in bloque:
            return "Eliminado"
        return "No disponible"

    def _extraer_rut(self, bloque):
        match = re.search(r"(\d{7,8}-\d)", bloque)
        if match:
            rut = match.group(1)
            rut_partes = rut.split('-')
            numero_rut = rut_partes[0]
            digito_verificador = rut_partes[1]
            # Añadir puntos a los miles
            numero_rut_formateado = "{:,}".format(int(numero_rut)).replace(",", ".")
            return f"{numero_rut_formateado}-{digito_verificador}"
        else:
            return "No disponible"

    def _extraer_nombre(self, bloque):
        match = re.search(r"N\s+([A-ZÁÉÍÓÚÑ ]+)\s+([A-ZÁÉÍÓÚÑ ]+)\s+([A-ZÁÉÍÓÚÑ ]+)", bloque)
        if match:
            nombre_completo = " ".join(match.groups())
            # Extraer los dos últimos caracteres del nombre
            ultimos_dos_caracteres = nombre_completo[:-2]
            return ultimos_dos_caracteres.rstrip()  # Eliminar espacios a la derecha
        else:
            return "No disponible"

    def _extraer_direccion(self, bloque):
        match = re.search(r"Dirección Particular:\s+([^\n]+)", bloque)
        return match.group(1).strip() if match else "No disponible"

    def _extraer_email(self, bloque):
        match = re.search(r"Email:\s+([^\n]+)", bloque)
        return match.group(1).strip() if match else "No disponible"

    def _extraer_telefono(self, bloque):
        match = re.search(r"Teléfono:\s+([^\n]+)", bloque)
        return match.group(1).strip() if match else "No disponible"

    def _extraer_fecha_nacimiento(self, bloque, sujeto):
        # Extrae la fecha de nacimiento solo si el sujeto es Niño, Niña o Adolescente
        if sujeto.lower() in ["niño", "niña", "adolescente"]:
            match = re.search(r"(\d{2}/\d{2}/\d{4})\s+(\d{1,2}\s+años)", bloque)
            if match:
                fecha_nacimiento = match.group(1)
                edad = match.group(2)
                return fecha_nacimiento, edad
        return None, None

    def discriminar_datos(self, registro):
        # Solo mostramos ciertos datos dependiendo del tipo de sujeto
        if registro.sujeto.lower() in ["niño", "niña", "adolescente"]:
            return {
                "Nombre Completo": registro.nombre,
                "Run": registro.rut,
                "Fecha de Nacimiento": registro.fecha_nacimiento,
                "Edad": registro.edad
            }
        elif registro.sujeto.lower() in ["dte", "ddo", "dnte", "dndo"]:
            return {
                "Nombre Completo": registro.nombre,
                "Run": registro.rut,
                "Domicilio": registro.direccion,
                "Teléfono": registro.telefono,
                "Email": registro.email
            }
        else:
            return {
                "Nombre Completo": registro.nombre
            }

    def presentar_datos_en_columnas(self):
        # Presenta los datos en dos columnas: Sujeto y Estado | Información relevante
        litigantes=[]
        for registro in self.registros:
            sujeto_estado = f"{registro.sujeto} - {registro.estado}"
            datos = self.discriminar_datos(registro)
            litigantes.append({'sujeto':sujeto_estado, 'dato':datos})
            #print(f"{sujeto_estado:<30} | {datos}")
        return litigantes
    def obtener_registros(self):
        return self.registros


# Ejemplo de uso:
texto = """ 

Confirmado  Reqte.  20045629-7 N YANIRA DENISE  COLILLANCA  VALENCIA   No  F No  ---  Chilena 18/08/1998 26 años --- --- S 
  Dirección Particular: Presidente Eisenhower 109 , LA GRANJA  Email: cyaniradenisse@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  NIÑA  25050050-5 N MARTINA ANTONELLA  RODRÍGUEZ  VALENCIA   No  F Historial del Menor Historial Fichas     Chilena 20/07/2015 9 años --- --- S 
  Dirección Particular: TOMÉ 0943 , LA GRANJA  Email: No posee Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  Reqdo.  15792517-2 N VALESCA DEL CARMEN  VALENCIA  ROJAS   No  F No  ---  Chilena 21/09/1984 40 años --- --- S 
  Dirección Particular: TOMÉ 943 , LA GRANJA  Email: valescavalenciarojas@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  Reqdo.  13702263-K N RENÉ HERNÁN  RODRÍGUEZ  BERRÍOS   No  M No  ---  Chilena 03/06/1978 46 años --- --- S 
  Dirección Particular: INCA DE ORO 7946 , LA GRANJA  Email: chicorene51@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  Curador Ad-Litem   16353568-8 N DIEGO ALEJANDRO  MUÑOZ  MALDONADO   No  M No  ---  Chilena 15/07/1986 38 años --- --- S 
  Dirección Particular: a , SAN MIGUEL  Email: notificacreden1@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  APOD.  19796330-1 N ESTEFANÍA ARACELY  HERNÁNDEZ  RIQUELME   No  F No  ---  --- 25/09/1997 27 años --- --- S  
  Dirección Particular: Ramón Subercaseux 1510 , SAN MIGUEL  Email: notificacreden1@gmail.com Teléfono: 355354858    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: --- Género: --- 
Confirmado  Curador Ad-Litem   10301933-8 N AARON RODRIGO  VEGA  SÁNCHEZ   No  M No  ---  Chilena 08/04/1970 54 años 26/04/1995 --- C 
  Dirección Particular: No posee  Email: notificacreden1@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  Curador Ad-Litem   15845206-5 N KARIN LIZ  WEBER  DÍAZ   No  F No  ---  Chilena 01/02/1985 39 años --- --- S 
  Dirección Particular: No posee  Email: notificacreden1@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Por Confirmar  Curador Ad-Litem   17354242-9 N VALENTINA  MAFUCCI  ELLIES   No  F No  ---  Chilena 17/11/1989 34 años 11/01/2020 --- C 
  Dirección Particular: No posee  Email: notificacreden1@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  TERC.  2021-4 N MEJOR  NIÑEZ  RM   No  . No  ---  --- --- --- --- --- --- 
  Dirección Particular: No posee  Email: metropolitana@servicioproteccion.gob.cl Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
   TERC.  0-0 J DAM LA CISTERNA       No  . No  ---  --- --- --- --- --- --- 
  Dirección Particular: , , LA CISTERNA  Email: ftcsdamlacisterna2@gmail.com Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: No tiene Género: Sin definir 
Confirmado  Reqte.  17926991-0 N JENNIFER PATRICIA  ESPINOZA  VIDAL   No  F No  ---  --- --- --- --- --- --- 
  Dirección Particular: No posee  Email: No posee Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: --- Género: --- 
Confirmado  APOD.  20255268-4 N DANIELA CATALINA  SALGADO  ARANEDA   No  F No  ---  --- --- --- --- --- --- 
  Dirección Particular: No posee  Email: No posee Teléfono: No posee    
  País: ---  Migrante: NO  Pobreza: NO P. Originario: NO  Disc.: --- Género: ---
  
  """

extractor = ExtractorDeRegistros(texto)
extractor.extraer_datos()

# Obtener los registros extraídos
registros = extractor.obtener_registros()

# Presentar los datos en dos columnas
extractor.presentar_datos_en_columnas()
print(registros)

