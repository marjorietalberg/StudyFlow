import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_SURFACE, COLOR_BORDER
)


class Sidebar(ft.Container):
    def __init__(self, on_page_change, current_page: str = "dashboard"):
        super().__init__()
        self.on_page_change = on_page_change
        self.current_page = current_page
        self.width = 250
        self.bgcolor = COLOR_SURFACE
        self.border = ft.border.only(right=ft.BorderSide(1, COLOR_BORDER))
        self.padding = ft.padding.all(16)

        self.menu_items = [
            ("dashboard", "Dashboard", ft.Icons.DASHBOARD_ROUNDED),
            ("quadros", "Meus Quadros", ft.Icons.DASHBOARD_CUSTOMIZE_ROUNDED),
            ("kanban", "Quadro Kanban", ft.Icons.VIEW_KANBAN_ROUNDED),
            ("atividades", "Minhas Atividades", ft.Icons.CHECKLIST_ROUNDED),
            ("calendario", "Agenda & Calendário", ft.Icons.CALENDAR_MONTH_ROUNDED),
            ("categorias", "Categorias & Tags", ft.Icons.LABEL_ROUNDED),
            ("concluidas", "Atividades Concluídas", ft.Icons.CHECK_CIRCLE_ROUNDED),
        ]

        self.content = self._build_content()

    def set_current_page(self, page_name: str):
        self.current_page = page_name
        self.content = self._build_content()
        self.update()

    def _build_menu_button(self, page_id: str, label: str, icon_name):
        is_active = (self.current_page == page_id)

        bg = COLOR_PRIMARY_LIGHT if is_active else ft.Colors.TRANSPARENT
        text_col = COLOR_PRIMARY if is_active else COLOR_TEXT_SECONDARY
        icon_col = COLOR_PRIMARY if is_active else COLOR_TEXT_SECONDARY
        font_w = ft.FontWeight.W_600 if is_active else ft.FontWeight.W_400

        def on_click(e):
            self.current_page = page_id
            self.content = self._build_content()
            self.update()
            if self.on_page_change:
                self.on_page_change(page_id)

        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon_name, size=20, color=icon_col),
                    ft.Text(label, size=13, weight=font_w, color=text_col),
                ],
                spacing=12,
                alignment=ft.MainAxisAlignment.START,
            ),
            bgcolor=bg,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            ink=True,
            on_click=on_click,
        )

    def _build_content(self):
        # 1. Header do Logo
        brand_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=ft.Colors.WHITE, size=18),
                    bgcolor=COLOR_PRIMARY,
                    border_radius=8,
                    padding=ft.padding.all(7),
                ),
                ft.Column(
                    controls=[
                        ft.Text("DayFlow", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                        ft.Text("Gerenciador Visual", size=10, color=COLOR_TEXT_SECONDARY),
                    ],
                    spacing=0,
                ),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )

        # 2. Itens de Navegação Principal
        nav_controls = []
        for pid, label, icon in self.menu_items:
            nav_controls.append(self._build_menu_button(pid, label, icon))

        # 3. Rodapé de Perfil e Swagger
        swagger_btn = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.API_ROUNDED, size=18, color=COLOR_PRIMARY),
                    ft.Text("Documentação Swagger", size=12, weight=ft.FontWeight.W_500, color=COLOR_PRIMARY),
                ],
                spacing=10,
            ),
            bgcolor=COLOR_PRIMARY_LIGHT,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            ink=True,
            on_click=lambda e: e.page.launch_url("http://127.0.0.1:8000/docs"),
        )

        user_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.CircleAvatar(
                        content=ft.Text("DF", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        bgcolor=COLOR_PRIMARY,
                        radius=16,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("Usuário DayFlow", size=12, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                            ft.Text("Plano Pro Local", size=10, color=COLOR_TEXT_SECONDARY),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=10,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=10,
            padding=ft.padding.all(8),
        )

        return ft.Column(
            controls=[
                brand_row,
                ft.Divider(height=16, color=COLOR_BORDER),
                ft.Text("MENU PRINCIPAL", size=10, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY),
                ft.Column(controls=nav_controls, spacing=4),
                ft.Container(expand=True),  # Espaço flexível
                swagger_btn,
                user_card,
            ],
            spacing=10,
            expand=True,
        )
