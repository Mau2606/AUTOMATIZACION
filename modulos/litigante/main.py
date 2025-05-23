import flet as ft
from functools import partial

# Descomenta la siguiente línea si guardaste la lógica en logic.py
from logic import Registro, ExtractorDeRegistros
# Si no, asegúrate que las clases Registro y ExtractorDeRegistros
# estén definidas *antes* de la función main en este mismo archivo.


def main(page: ft.Page):
    page.title = "Extractor y Formateador de Registros"
    page.window.min_width = 700 # Establecer un ancho mínimo
    page.window.min_height = 600 # Establecer una altura mínima

    # --- Theme Setup ---
    page.theme_mode = ft.ThemeMode.SYSTEM # Adapta a OS (o usa DARK/LIGHT)
    # Usar un color base para generar el esquema de colores
    page.theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE_GREY,
        use_material3=True, # Usar Material Design 3
        # Personalizaciones opcionales (ejemplo):
        # text_theme=ft.TextTheme(body_medium=ft.TextStyle(size=13))
    )
    page.dark_theme = ft.Theme(
        color_scheme_seed=ft.colors.BLUE_GREY,
        use_material3=True,
        #brightness=ft.Brightness.DARK
    )
    page.vertical_alignment = ft.MainAxisAlignment.START

    # --- Referencias a Controles ---
    # Crear las instancias de los controles aquí para poder referenciarlas fácilmente
    txt_input = ft.TextField(
        label="Pegue el texto completo aquí",
        hint_text="El texto que contiene los registros a extraer...",
        multiline=True,
        min_lines=20, # Ajustar según necesidad
        expand=True, # Clave para que ocupe el espacio vertical en su columna
        border_color=ft.colors.OUTLINE_VARIANT,
        keyboard_type=ft.KeyboardType.MULTILINE,
        border_radius=ft.border_radius.all(8),
    )
    lv_results = ft.ListView(expand=True, spacing=8, auto_scroll=True) # auto_scroll para ir al final


    # --- Event Handlers ---
    def mostrar_snackbar(mensaje, es_error=False):
        page.open(
             ft.SnackBar(
                content=ft.Text(mensaje),
                bgcolor=ft.colors.ERROR_CONTAINER if es_error else ft.colors.SECONDARY_CONTAINER,
                #content_color=ft.colors.ON_ERROR_CONTAINER if es_error else ft.colors.ON_SECONDARY_CONTAINER,
                open=True
            )
        )

    def copiar_al_portapapeles(texto_a_copiar, e):
        page.set_clipboard(texto_a_copiar)
        print(f"Copiado: {texto_a_copiar[:100]}...") # Log corto
        mostrar_snackbar("Texto copiado al portapapeles!")
        # page.update() # SnackBar debe actualizar por sí mismo

    def clear_all(e):
        txt_input.value = ""
        lv_results.controls.clear()
        txt_input.focus() # Poner foco de nuevo en el input
        mostrar_snackbar("Campos limpiados.")
        page.update() # Actualizar la UI

    def formatear_texto(e):
        texto_original = txt_input.value
        if not texto_original:
            mostrar_snackbar("Por favor, pega el texto en el cuadro de la izquierda.", es_error=True)
            return

        extractor = ExtractorDeRegistros(texto_original)
        try:
            extractor.extraer_datos()
            resultados = extractor.discriminar_y_formatear_datos()
        except Exception as ex:
             mostrar_snackbar(f"Error al procesar el texto: {ex}", es_error=True)
             print(f"Error detallado formateando: {ex}") # Log de error
             lv_results.controls.clear()
             lv_results.controls.append(ft.Text("Ocurrió un error durante el procesamiento.", color=ft.colors.ERROR))
             page.update()
             return

        lv_results.controls.clear() # Limpiar resultados anteriores

        if not resultados:
            lv_results.controls.append(
                ft.Container(
                    content=ft.Text("No se encontraron registros válidos en el texto.", italic=True, color=ft.colors.OUTLINE),
                    padding=10
                )
            )
        else:
            print(f"Formateo exitoso: {len(resultados)} registros encontrados.") # Log
            for resultado in resultados:
                texto_a_copiar = resultado['info_para_copiar']

                boton_copiar = ft.IconButton(
                    icon=ft.icons.COPY_ROUNDED, # Icono actualizado
                    tooltip="Copiar este registro",
                    on_click=partial(copiar_al_portapapeles, texto_a_copiar),
                    icon_size=18,
                    icon_color=ft.colors.SECONDARY # Color del icono
                )

                # Contenedor para cada resultado con estilo mejorado
                item_resultado = ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [
                                    # Título del registro (Sujeto - Estado)
                                    ft.Text(
                                        resultado['sujeto_estado'],
                                        weight=ft.FontWeight.BOLD,
                                        size=14,
                                        color=ft.colors.PRIMARY # Color primario para el título
                                    ),
                                    boton_copiar # Botón de copiar alineado a la derecha
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            # Información formateada (texto principal)
                            ft.Text(
                                texto_a_copiar,
                                selectable=True,
                                size=12.5, # Tamaño de fuente ligeramente ajustado
                                color=ft.colors.ON_SURFACE_VARIANT # Color de texto secundario
                            )
                        ],
                        spacing=6, # Espacio entre título e info
                        tight=True # Ajustar el tamaño vertical al contenido
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10), # Padding interno
                    border=ft.border.all(1, ft.colors.OUTLINE_VARIANT), # Borde sutil
                    border_radius=ft.border_radius.all(10), # Bordes más redondeados
                    bgcolor=ft.colors.SURFACE_VARIANT, # Color de fondo suave
                    margin=ft.margin.only(bottom=6) # Espacio entre contenedores de resultados
                )
                lv_results.controls.append(item_resultado)

        mostrar_snackbar(f"{len(resultados)} registros procesados.")
        page.update()

    # --- Definición de Controles (ya creados arriba) ---
    # Botones principales
    btn_formatear = ft.ElevatedButton(
        text="Formatear Texto",
        icon=ft.icons.FORMAT_ALIGN_LEFT_ROUNDED,
        on_click=formatear_texto,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)) # Estilo de botón
    )

    btn_clear = ft.OutlinedButton( # Estilo diferente para Limpiar
        text="Limpiar",
        icon=ft.icons.CLEAR_ROUNDED,
        on_click=clear_all,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)) # Estilo de botón
    )


    # --- Layout Principal ---

    # AppBar
    page.appbar = ft.AppBar(
        title=ft.Text("Extractor y Formateador"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT, # Color de fondo consistente
        elevation=2 # Sombra ligera
        # Actions se pueden agregar aquí si se desea, pero el botón limpiar está abajo
    )

    # Columna Izquierda: Input y Botones (AHORA A LA IZQUIERDA)
    columna_input = ft.Column(
        [
            ft.Text("Texto Original:", weight=ft.FontWeight.BOLD, size=16),
            txt_input, # El TextField se expande aquí
            ft.Row( # Fila para los botones debajo del input
                [btn_formatear, btn_clear],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY, # Espaciar botones
            )
        ],
        expand=True, # Ocupa el espacio vertical asignado por el Container padre
        spacing=12, # Espacio entre elementos de la columna
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH # Estira el TextField horizontalmente
    )

    # Columna Derecha: Resultados (AHORA A LA DERECHA)
    columna_resultados = ft.Column(
        [
            ft.Text("Resultados Formateados:", weight=ft.FontWeight.BOLD, size=16),
            lv_results # ListView se expande aquí
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        spacing=12
    )

    # Layout Principal (Contenedores Swapped)
    layout_principal = ft.Row(
        [
            # Contenedor Izquierdo (Input)
            ft.Container(
                content=columna_input,
                expand=3, # Darle más espacio al input (ajustar proporción 3:2)
                padding=15,
                # border_radius=ft.border_radius.all(10), # Opcional: redondear contenedor
                # bgcolor=ft.colors.SURFACE, # Opcional: color de fondo
            ),
            ft.VerticalDivider(width=1, thickness=1),
            # Contenedor Derecho (Resultados)
            ft.Container(
                content=columna_resultados,
                expand=2, # Menos espacio para resultados (ajustar proporción 3:2)
                padding=15,
                # border_radius=ft.border_radius.all(10),
                # bgcolor=ft.colors.SURFACE,
            )
        ],
        expand=True, # La fila ocupa todo el espacio de la página
        vertical_alignment=ft.CrossAxisAlignment.STRETCH # Estira las columnas hijas
    )

    page.add(layout_principal)
    page.update() # Asegura renderizado inicial

# --- Ejecutar la aplicación ---
if __name__ == "__main__":
    ft.app(target=main)