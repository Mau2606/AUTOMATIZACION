import flet as ft

class SeleccionPasoAPaso:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Medidas Cautelares"
        self.page.window.width = 600
        self.page.window.height = 400
        self.page.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.page.window.center()
        self.page.window.maximizable = False
        self.page.window.resizable = False

        self.selecciones = []
        self.paso = 1

        self.btn_vif = ft.ElevatedButton(
            "VIF",
            bgcolor=ft.colors.LIGHT_BLUE_500,
            color=ft.colors.BLACK,
            width=self.page.window.width,
            height=40,
            on_click=self.siguiente_paso_vif,
        )
        self.btn_genero = ft.ElevatedButton(
            "VIF Género",
            bgcolor=ft.colors.LIGHT_GREEN_500,
            color=ft.colors.BLACK,
            width=self.page.window.width,
            height=40,
            on_click=self.siguiente_paso_genero,
        )
        self.btn_proteccion = ft.ElevatedButton(
            "Protección",
            bgcolor=ft.colors.DEEP_ORANGE_200,
            color=ft.colors.BLACK,
            width=self.page.window.width,
            height=40,
            on_click=self.siguiente_paso_proteccion,
        )

        self.selecciones_text = ft.Text("")

        self.mostrar_paso1()

    def siguiente_paso_vif(self, e):
        self.selecciones.append("VIF")
        self.mostrar_paso_vif()
        self.actualizar_selecciones()

    def siguiente_paso_genero(self, e):
        self.selecciones.append("VIF Género")
        self.mostrar_paso_genero()
        self.actualizar_selecciones()

    def siguiente_paso_proteccion(self, e):
        self.selecciones.append("Protección")
        self.mostrar_paso_proteccion()
        self.actualizar_selecciones()

    def mostrar_paso1(self):
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    self.btn_vif,
                    self.btn_genero,
                    self.btn_proteccion,
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=30,
            )
        )

    def mostrar_paso_vif(self):
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("Paso VIF: Selecciona opciones específicas de VIF."),
                    ft.ElevatedButton("Incompetencia Ministerio Público", on_click=self.incompetencia_mp),
                    ft.ElevatedButton("Citación a audiencia preparatoria", on_click=self.citacion_audiencia),
                    ft.Row(
                        [
                            ft.Text("Selecciones:"),
                            self.selecciones_text,
                            ft.ElevatedButton("Volver", on_click=lambda _: self.mostrar_paso1()),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        expand=False,
                    )
                ],
                expand=True,
            )
        )

    def incompetencia_mp(self, e):
        self.selecciones.append("Incompetencia Ministerio Público")
        self.actualizar_selecciones()
        self.page.add(ft.Text("Has seleccionado Incompetencia Ministerio Público"))

    def citacion_audiencia(self, e):
        self.selecciones.append("Citación a audiencia preparatoria")
        self.actualizar_selecciones()
        self.page.add(ft.Text("Has seleccionado Citación a audiencia preparatoria"))

    def mostrar_paso_genero(self):
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("Paso VIF Género: Selecciona opciones específicas de VIF Género."),
                    ft.Row(
                        [
                            ft.Text("Selecciones:"),
                            self.selecciones_text,
                            ft.ElevatedButton("Volver", on_click=lambda _: self.mostrar_paso1()),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        expand=False,
                    ),
                ],
                expand=True,
            )
        )

    def mostrar_paso_proteccion(self):
        self.page.clean()
        self.page.add(
            ft.Column(
                [
                    ft.Text("Paso Protección: Selecciona opciones específicas de Protección."),
                    ft.Row(
                        [
                            ft.Text("Selecciones:"),
                            self.selecciones_text,
                            ft.ElevatedButton("Volver", on_click=lambda _: self.mostrar_paso1()),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        expand=False,
                    ),
                ],
                expand=True,
            )
        )

    def actualizar_selecciones(self):
        self.selecciones_text.value = ", ".join(self.selecciones)
        self.page.update()

    def main(page: ft.Page):
        SeleccionPasoAPaso(page)

if __name__ == "__main__":
    ft.app(target=SeleccionPasoAPaso.main)