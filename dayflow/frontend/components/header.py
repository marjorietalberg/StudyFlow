import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_SURFACE, COLOR_BORDER
)


class Header(ft.Container):
    def __init__(self, title: str, subtitle: str, on_new_task=None, on_refresh=None):
        super().__init__()
        self.title_text = title
        self.subtitle_text = subtitle
        self.on_new_task = on_new_task
        self.on_refresh = on_refresh
        self.height = 70
        self.bgcolor = COLOR_SURFACE
        self.border = ft.border.only(bottom=ft.BorderSide(1, COLOR_BORDER))
        self.padding = ft.padding.symmetric(horizontal=24, vertical=12)

        self.content = self._build_content()

    def update_header(self, title: str, subtitle: str):
        self.title_text = title
        self.subtitle_text = subtitle
        self.content = self._build_content()
        self.update()

    def _build_content(self):
        title_col = ft.Column(
            controls=[
                ft.Text(self.title_text, size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                ft.Text(self.subtitle_text, size=11, color=COLOR_TEXT_SECONDARY),
            ],
            spacing=2,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        actions_row = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.REFRESH_ROUNDED,
                    icon_color=COLOR_TEXT_SECONDARY,
                    tooltip="Recarregar dados da API",
                    on_click=lambda e: self.on_refresh() if self.on_refresh else None,
                ),
                ft.ElevatedButton(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.ADD_ROUNDED, size=18, color=ft.Colors.WHITE),
                            ft.Text("Nova Atividade", size=13, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                        ],
                        spacing=6,
                    ),
                    bgcolor=COLOR_PRIMARY,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    ),
                    on_click=lambda e: self.on_new_task() if self.on_new_task else None,
                ),
            ],
            spacing=12,
            alignment=ft.MainAxisAlignment.END,
        )

        return ft.Row(
            controls=[
                title_col,
                ft.Container(expand=True),
                actions_row,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
