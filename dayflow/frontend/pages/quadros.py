import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER, COLOR_DANGER
)
from api_client import api
from components.modals import open_novo_quadro_modal, open_confirmacao_modal, show_snackbar


class QuadrosPage(ft.Container):
    def __init__(self, page: ft.Page, on_open_board=None):
        super().__init__()
        self.flet_page = page
        self.on_open_board = on_open_board
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = ft.padding.all(24)

        self.content = self._build_view()

    def refresh(self):
        self.content = self._build_view()
        self.update()

    def _build_board_card(self, q):
        qid = q["id"]
        nome = q.get("nome", "Quadro")
        desc = q.get("descricao") or "Sem descrição."
        cor = q.get("cor") or COLOR_PRIMARY
        total_atvs = q.get("total_atividades", 0)
        concluidas = q.get("total_concluidas", 0)
        pct = q.get("percentual_conclusao", 0.0)
        prog_val = (pct / 100.0) if total_atvs > 0 else 0.0

        def on_abrir(e):
            if self.on_open_board:
                self.on_open_board(qid)

        def on_excluir(e):
            def confirmar(ev):
                self.flet_page.pop_dialog()
                res, err = api.delete_quadro(qid)
                if err:
                    show_snackbar(self.flet_page, f"Erro ao excluir quadro: {err}", is_error=True)
                else:
                    show_snackbar(self.flet_page, f"Quadro '{nome}' removido.")
                    self.refresh()

            open_confirmacao_modal(
                self.flet_page,
                f"Excluir quadro '{nome}'?",
                "Todas as listas e atividades vinculadas a este quadro serão permanentemente apagadas.",
                confirmar
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Faixa superior de cor personalizada
                    ft.Container(height=6, bgcolor=cor, border_radius=ft.border_radius.only(top_left=12, top_right=12)),
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    controls=[
                                        ft.Text(nome, size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY, expand=True),
                                        ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_size=18, icon_color=COLOR_TEXT_SECONDARY, tooltip="Excluir Quadro", on_click=on_excluir),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.Text(desc, size=12, color=COLOR_TEXT_SECONDARY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Divider(color=COLOR_BORDER, height=12),
                                ft.Row(
                                    controls=[
                                        ft.Text(f"{total_atvs} Atividades", size=11, weight=ft.FontWeight.W_600, color=COLOR_TEXT_SECONDARY),
                                        ft.Text(f"{pct}% Concluído", size=11, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                                    ],
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                ft.ProgressBar(value=prog_val, color=cor, bgcolor=COLOR_PRIMARY_LIGHT, height=6),
                                ft.Container(height=4),
                                ft.ElevatedButton(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.VIEW_KANBAN_ROUNDED, size=16, color=ft.Colors.WHITE),
                                        ft.Text("Abrir Quadro Kanban", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                                    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
                                    bgcolor=cor,
                                    on_click=on_abrir,
                                ),
                            ],
                            spacing=6,
                        ),
                        padding=ft.padding.all(16),
                    )
                ],
                spacing=0,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            width=320,
        )

    def _build_view(self):
        quadros, err = api.get_quadros()
        quadros = quadros or []

        header_bar = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text("Meus Quadros de Atividades", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                        ft.Text("Organize seus projetos, estudos e rotinas em quadros visuais inspirados no Trello.", size=12, color=COLOR_TEXT_SECONDARY),
                    ],
                    spacing=2,
                ),
                ft.ElevatedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.ADD_ROUNDED, size=16, color=ft.Colors.WHITE),
                        ft.Text("Novo Quadro", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                    ], spacing=6),
                    bgcolor=COLOR_PRIMARY,
                    on_click=lambda e: open_novo_quadro_modal(self.flet_page, self.refresh),
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        grid_controls = [self._build_board_card(q) for q in quadros]

        return ft.Column(
            controls=[
                header_bar,
                ft.Divider(color=COLOR_BORDER, height=16),
                ft.Row(
                    controls=grid_controls,
                    wrap=True,
                    spacing=16,
                    run_spacing=16,
                ) if grid_controls else ft.Text("Nenhum quadro cadastrado. Crie seu primeiro quadro acima!", size=13, color=COLOR_TEXT_SECONDARY),
            ],
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
