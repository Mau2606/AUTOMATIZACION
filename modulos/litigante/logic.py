# logic.py (o al inicio de tu archivo principal)
import re
from datetime import datetime

class Registro:
    def __init__(self, sujeto, nombre, rut, direccion, email, telefono, estado, fecha_nacimiento=None, edad=None):
        self.sujeto = sujeto if sujeto else "Desconocido"
        self.nombre = nombre if nombre else "No disponible"
        self.rut = rut if rut else "No disponible"
        self.direccion = direccion if direccion else "No disponible"
        self.email = email if email else "No disponible"
        self.telefono = telefono if telefono else "No disponible"
        self.estado = estado if estado else "Desconocido"
        self.fecha_nacimiento = fecha_nacimiento # Puede ser None
        self.edad = edad # Puede ser None

    def __repr__(self):
        # Representación básica para debugging
        return (f"Sujeto: {self.sujeto}, Nombre: {self.nombre}, RUT: {self.rut}, Estado: {self.estado}")

class ExtractorDeRegistros:
    def __init__(self, texto):
        self.texto = texto if texto else ""
        self.registros = []

    def extraer_datos(self):
        self.registros = []
        # Patrón para encontrar bloques iniciados por Estado + Sujeto + RUT/ID
        # Captura: 1:Estado, 2:Sujeto, 3:RUT/ID, 4:Resto de la línea 1, 5:Línea Dirección, 6:Línea Email, 7:Línea Teléfono
        # Se asume que Dirección, Email, Teléfono están en líneas separadas que comienzan con esa palabra clave.
        # Este patrón es complejo y puede necesitar ajustes según variaciones del texto.
        # Usamos re.finditer para procesar cada match como un bloque potencial.

        # Primero, limpiamos un poco el texto para manejar saltos de línea inconsistentes
        texto_limpio = re.sub(r'\s*\n\s*', '\n', self.texto.strip())

        # Dividimos el texto en posibles bloques basados en los estados conocidos
        # Usamos un lookahead positivo para mantener el delimitador (estado) al inicio de cada bloque
        # Regex más simple para dividir: busca un estado al inicio de una línea (con posible espacio antes)
        bloques_potenciales = re.split(r'(?=\n?(?:Confirmado|Pendiente|Eliminado|Por Confirmar)\s+)', texto_limpio)

        for bloque_raw in bloques_potenciales:
            bloque = bloque_raw.strip()
            if not bloque:
                continue

            estado = self._extraer_estado(bloque)
            sujeto = self._extraer_sujeto(bloque)  # Extraer sujeto primero
            rut = self._extraer_rut(bloque)
            # Pasar 'sujeto' a _extraer_nombre:
            nombre = self._extraer_nombre(bloque, rut, sujeto)
            direccion = self._extraer_direccion(bloque)
            email = self._extraer_email(bloque)
            telefono = self._extraer_telefono(bloque)
            fecha_nacimiento, edad = self._extraer_fecha_nacimiento(bloque)

            # Validar si se extrajo información mínima (al menos un sujeto y estado)
            if sujeto != "Desconocido" or estado != "Desconocido":
                 registro = Registro(sujeto, nombre, rut, direccion, email, telefono, estado, fecha_nacimiento, edad)
                 self.registros.append(registro)

    def _extraer_estado(self, bloque):
        if bloque.startswith("Confirmado"): return "Confirmado"
        if bloque.startswith("Pendiente"): return "Pendiente de pronunciación"
        if bloque.startswith("Por Confirmar"): return "Pendiente de pronunciación" # Tratar igual que Pendiente
        if bloque.startswith("Eliminado"): return "Eliminado"
        # Buscar estado si no está al inicio (puede pasar con el primer bloque si no empieza con estado)
        match = re.search(r"^(Confirmado|Pendiente|Eliminado|Por Confirmar)", bloque)
        if match:
            estado_str = match.group(1)
            if estado_str == "Pendiente" or estado_str == "Por Confirmar":
                 return "Pendiente de pronunciación"
            return estado_str
        return "Desconocido" # Si no se encuentra

    def _extraer_sujeto(self, bloque):
        """
        Extrae el tipo de sujeto del bloque, manejando puntos y casos compuestos.
        """
        # Busca el sujeto después del estado y antes del RUT/ID. Permite puntos y espacios.
        # Prioriza matches más largos primero si hay ambigüedad.
        match = re.search(
            r"^(?:Confirmado|Pendiente|Eliminado|Por Confirmar)\s+"  # Estado
            r"([a-zA-ZÁÉÍÓÚÑüÜ.\s-]+\.?)"  # Sujeto (captura) - permite puntos, espacios, guiones
            r"\s+"  # Espacio separador
            r"(?:\d{1,8}-[\dkK]|\d+-\d+\s+[NJ]|0-0\s+J)",  # RUT o ID alternativo
            bloque
        )
        if match:
            # Limpiar espacios extra y puntos al final
            sujeto = match.group(1).strip().rstrip('.')
            # Corrección específica para evitar capturar parte del ID si el sujeto es corto
            if len(sujeto.split()[-1]) <= 2 and sujeto.split()[-1].isdigit():  # Ej: si capturó "Reqte 20"
                sujeto = " ".join(sujeto.split()[:-1])  # Quitar el número final

            return sujeto.strip()

        # Fallback específico para TERC. si el patrón principal falla
        match_terc = re.search(r"^(?:Confirmado|Pendiente|Eliminado|Por Confirmar)\s+(TERC\.)", bloque)
        if match_terc:
            return match_terc.group(1).strip()

        return "Desconocido"

    def _extraer_rut(self, bloque):
        """
        Extrae el RUT/RUN chileno del bloque de texto.
        Busca formatos con o sin puntos, asegurando capturar el número completo y DV.
        También maneja IDs alternativos específicos.
        """
        # Regex mejorada: busca RUT completo (con o sin puntos)
        # (?<!\d) -> No precedido por un dígito (evita capturas parciales)
        # \d{1,3}(?:\.?\d{3})* -> 1-3 dígitos iniciales, seguidos de grupos de (opcionalmente un punto y 3 dígitos)
        # -[\dkK] -> Guion seguido de un dígito o K/k
        # (?!\d) -> No seguido por un dígito (evita capturas parciales)
        match = re.search(r"(?<!\d)(\d{1,3}(?:\.?\d{3})*-[\dkK])(?!\d)", bloque)
        if match:
            rut_capturado = match.group(1)
            # Siempre intentar formatear el RUT capturado
            return self._formatear_rut(rut_capturado)

        # IDs alternativos (mantener separados, no formatear como RUT)
        match_alt = re.search(r"(\d+-\d+)\s+[NJ]", bloque)
        if match_alt:
            return match_alt.group(1)  # Ej: '2021-4'
        match_alt2 = re.search(r"(0-0)\s+J", bloque)
        if match_alt2:
            return match_alt2.group(1)  # Ej: '0-0'

        return "No disponible"

    def _formatear_rut(self, rut_capturado):
        """
        Formatea un string de RUT (que puede tener o no puntos)
        al formato estándar chileno: xx.xxx.xxx-K.
        """
        try:
            # 1. Limpiar el RUT: quitar puntos y guion, convertir K a mayúscula.
            rut_limpio = rut_capturado.replace(".", "").replace("-", "")
            if len(rut_limpio) < 2:
                return rut_capturado  # Devolver original si es muy corto

            dv = rut_limpio[-1].upper()  # Obtener DV y asegurar K mayúscula
            numero_str = rut_limpio[:-1]  # Obtener la parte numérica

            # 2. Validar que la parte numérica sea realmente un número
            if not numero_str.isdigit():
                # Si contiene algo que no sea dígito (raro, pero posible), devolver original
                return rut_capturado

            # 3. Convertir a entero para usar formato de miles
            numero_int = int(numero_str)

            # 4. Aplicar formato con comas y luego reemplazar por puntos
            # "{:,}" usa la configuración regional para el separador, pero lo forzamos a punto.
            numero_formateado = "{:,}".format(numero_int).replace(",", ".")

            # 5. Reconstruir el RUT formateado
            return f"{numero_formateado}-{dv}"

        except Exception as e:
            # Si ocurre cualquier error inesperado durante el formateo,
            # devolver el RUT original capturado para evitar perder el dato.
            print(f"Advertencia: No se pudo formatear el RUT '{rut_capturado}'. Error: {e}")
            return rut_capturado

    def _extraer_nombre(self, bloque, rut_o_id, sujeto):
        """
        Extrae nombre/organización usando un patrón SIMPLIFICADO que busca
        ' N ' o ' J ' seguido de palabras en mayúsculas, terminando justo antes de ' No F', ' No M', o ' No .'.
        """
        nombre_encontrado = None

        # Patrón Simplificado: Busca ' N ' o ' J ', captura texto en mayúsculas (.+?) de forma no-codiciosa,
        # hasta encontrar ' No ' seguido de F, M, o .
        # Se hace insensible a mayúsculas/minúsculas para ' N ' y ' J ', pero el nombre se espera en mayúsculas.
        # Se incluyen caracteres acentuados y ü/Ü.
        # NOTA: Este patrón ASUME que ' No F/M/.' SIEMPRE está presente después del nombre.
        patron_simple = r"\s[NJ]\s+([A-ZÁÉÍÓÚÑÜ\s]+?)\s+No\s+[FM.]"
        match_simple = re.search(patron_simple, bloque, re.IGNORECASE)  # Ignorar case para N/J

        if match_simple:
            # El grupo 1 contiene las palabras en mayúsculas capturadas
            nombre_encontrado = match_simple.group(1).strip()
            # Asegurarnos de no haber capturado espacios extra al final si los hubiera antes de ' No '
            nombre_encontrado = nombre_encontrado.strip()
            # print(f"DEBUG Nombre (Patrón Simple): '{nombre_encontrado}' para {sujeto} {rut_o_id}")
        else:
            # Si el patrón simple no funciona, no intentamos más nada en esta versión
            # print(f"DEBUG Nombre NO encontrado (Patrón Simple) para {sujeto} {rut_o_id}")
            pass  # nombre_encontrado sigue siendo None

        # Devolver el nombre encontrado o "No disponible"
        return nombre_encontrado if nombre_encontrado else "No disponible"

    def _extraer_direccion(self, bloque):
        #match = re.search(r"Dirección Particular:\s+([^\n]+)", bloque, re.IGNORECASE)
        match = re.search(r"Dirección Particular:\s+(.*?)(?=\s*Email:)", bloque, re.IGNORECASE)

        return match.group(1).strip() if match else "No disponible"

    def _extraer_email(self, bloque):
        match = re.search(r"Email:\s+([^\s\n]+@[^\s\n]+\.[^\s\n]+)", bloque, re.IGNORECASE)
        return match.group(1).strip() if match else "No disponible"

    def _extraer_telefono(self, bloque):
        # Busca Teléfono: seguido de números o "No posee"
        match = re.search(r"Teléfono:\s+([\d\s+-]+|No posee)", bloque, re.IGNORECASE)
        if match:
             telefono = match.group(1).strip()
             # Evitar devolver "No posee" como un teléfono válido
             return telefono if telefono.lower() != "no posee" else "No disponible"
        return "No disponible"

    def _extraer_fecha_nacimiento(self, bloque):
         # Extrae fecha y edad si están presentes juntas
        match = re.search(r"(\d{2}/\d{2}/\d{4})\s+(\d{1,3}\s+años?)", bloque)
        if match:
            fecha_nacimiento_str = match.group(1)
            edad_str = match.group(2)
            # Validar fecha (opcional pero recomendado)
            try:
                datetime.strptime(fecha_nacimiento_str, '%d/%m/%Y')
                return fecha_nacimiento_str, edad_str
            except ValueError:
                return None, None # Fecha inválida
        return None, None # No encontrado

    def _dato_o_default(self, dato, default_text="NO REGISTRA"):
         """
         Devuelve el dato si es válido, o el texto por defecto si no lo es.
         Considera None, 'No disponible', 'No posee', cadenas vacías o solo espacios/comas.
         """
         if dato and str(dato).strip() and str(dato).strip().lower() not in ["no disponible", "no posee", ",",
                                                                             ", ,"]:
             return str(dato).strip()
         else:
             return default_text

    def discriminar_y_formatear_datos(self):
        """
        Procesa los registros extraídos, discrimina por tipo de sujeto y genera
        un string formateado específico para copiar, usando 'NO REGISTRA' para datos faltantes.
        Corrige la lógica para abogados/curadores para mostrar solo el nombre.
        """
        resultados_formateados = []
        for registro in self.registros:
            # Normalizar sujeto: lower, strip, quitar puntos para comparación
            sujeto_norm = registro.sujeto.lower().replace('.', '').strip()

            info_parts = []  # Lista para construir el string final

            # Obtener datos usando el helper _dato_o_default
            # NOTA: _extraer_nombre ahora devuelve "No disponible" si falla,
            # que _dato_o_default convertirá a "NO REGISTRA NOMBRE".
            nombre = self._dato_o_default(registro.nombre, "NO REGISTRA NOMBRE")
            run = self._dato_o_default(registro.rut)
            domicilio = self._dato_o_default(registro.direccion)
            email = self._dato_o_default(registro.email)
            telefono = self._dato_o_default(registro.telefono)
            fecha_nac = self._dato_o_default(registro.fecha_nacimiento)
            edad = self._dato_o_default(registro.edad)

            # --- Lógica de formato por tipo de sujeto ---
            grupo_demandantes = ["rqte", "dte", "dnte", "reqte", "reqdo", "ddo", "dndo", "solicitante","solicitado", "victima"]
            grupo_nna = ["niño", "niña", "adolescente", "nna"]
            grupo_abogados_curadores = ["ab dte", "ab ddo", "ap dte", "ap ddo", "apod", "curador ad-litem", "curador", "abg solici"]

            # --- ESTRUCTURA IF/ELIF/ELSE CORREGIDA ---
            if sujeto_norm in grupo_demandantes:
                info_parts.append(nombre)
                info_parts.append(f"RUN {run}")
                info_parts.append(f"DOM: {domicilio}\n")
                info_parts.append(f"EMAIL:{email}\n")
                info_parts.append(f"FONO: {telefono}")

            elif sujeto_norm in grupo_nna:
                info_parts.append(nombre)
                info_parts.append(f"RUN {run}")
                info_parts.append(f"NACID@ EL: {fecha_nac}")
                info_parts.append(f" {edad} AÑOS")

            elif sujeto_norm in grupo_abogados_curadores:
                # --- ¡CORRECCIÓN IMPORTANTE! ---
                # Para este grupo, SOLO queremos el nombre.
                # Usamos 'nombre' que ya pasó por _dato_o_default
                info_parts.append(nombre)
                # No añadir más nada a info_parts para este grupo.

            # Otros casos (TERC, desconocidos, etc.)
            else:
                info_parts.append(nombre)  # Nombre o Razón Social
                if run != "NO REGISTRA":
                    info_parts.append(f"RUT/ID: {run}")
                if email != "NO REGISTRA":
                    info_parts.append(f"EMAIL:{email}")
                if telefono != "NO REGISTRA":
                    info_parts.append(f"FONO: {telefono}")
                # Si solo quedó "NO REGISTRA NOMBRE" (porque es desconocido y sin datos)
                if len(info_parts) == 1 and info_parts[0] == "NO REGISTRA NOMBRE":
                    info_parts = ["Información detallada no aplicable o no extraída."]
                elif not info_parts:  # Si la lista está vacía
                    info_parts.append("Información detallada no aplicable o no extraída.")

            # --- Unir las partes ---
            # Filtrar partes vacías o nulas antes de unir
            info_string_final = ", ".join(part for part in info_parts if part and str(part).strip())

            # Asegurar que no quede vacío si todo falló
            if not info_string_final:
                info_string_final = "Información no disponible."

            # Resultado para este registro
            resultados_formateados.append({
                'sujeto_estado': f"{registro.sujeto} - {registro.estado}",
                'info_para_copiar': info_string_final
            })

        return resultados_formateados

    def obtener_registros(self):
        # Método para obtener los objetos Registro si es necesario fuera del formateo
        return self.registros

        # --- Añade esta función auxiliar DENTRO de la clase ExtractorDeRegistros ---
        def _dato_o_default(self, dato, default_text="NO REGISTRA"):
            """
            Devuelve el dato si es válido, o el texto por defecto si no lo es.
            Considera None, 'No disponible', 'No posee', cadenas vacías o solo espacios/comas.
            """
            if dato and str(dato).strip() and str(dato).strip().lower() not in ["no disponible", "no posee", ",",
                                                                                ", ,"]:
                return str(dato).strip()
            else:
                return default_text

