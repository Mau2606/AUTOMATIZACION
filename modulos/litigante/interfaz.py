# interfaz.py
import flet as ft
import pyperclip
from extractor import ExtractorDeRegistros

def crear_interfaz(page: ft.Page):
    page.bgcolor = ft.colors.BLUE_GREY_700
    page.title = "EasyLiti 1.0"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # Función para procesar el texto
    def procesar_texto(e):
        texto = campo_texto.value.strip()
        if texto:
            extractor = ExtractorDeRegistros(texto)
            extractor.extraer_datos()
            registros = extractor.presentar_datos_en_columnas()

            # Limpiamos la tabla
            tabla.rows.clear()
            print(registros)
            for registro in registros:
                fila = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(registro["sujeto"])),
                    #ft.DataCell(ft.Text(registro["datos"])),
                    #ft.DataCell(ft.IconButton(icon=ft.icons.COPY, on_click=lambda e, datos=registro["datos"]: copiar_al_portapapeles(datos)))
                ])
                tabla.rows.append(fila)

            tabla.update()
        else:
            print("sin texto que convertir")
    # Función para copiar al portapapeles
    def copiar_al_portapapeles(datos):
        pyperclip.copy(datos)
        page.snack_bar = ft.SnackBar(ft.Text("Datos copiados al portapapeles"))
        page.snack_bar.open = True
        page.update()

    # Elementos de la interfaz
    campo_texto = ft.TextField(label="Ingrese el texto aquí:", multiline=True, height=200,)
    boton_procesar = ft.ElevatedButton(text="Procesar", on_click=procesar_texto)

    # Definición de la tabla
    tabla = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Sujeto y Estado")),
            #ft.DataColumn(ft.Text("Datos Extraídos")),
            #ft.DataColumn(ft.Text("Copiar"))
        ],
        rows=[]
    )

    # Layout principal
    layout_principal = ft.Row(
        controls=[
            campo_texto,
            boton_procesar,
        ],
        alignment=ft.CrossAxisAlignment.CENTER.CENTER,
        spacing=20
    )

    layout_principal2 = ft.Row(
        controls=[
            tabla
        ],
        alignment=ft.CrossAxisAlignment.CENTER.CENTER,
        spacing=20
    )

    # Agregamos el layout a la página
    page.add(layout_principal, layout_principal2)
