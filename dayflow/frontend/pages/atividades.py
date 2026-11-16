import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER,
    COLOR_DANGER, COLOR_SUCCESS, COLOR_WARNING,
    PRIORITY_COLORS, STATUS_COLORS
)
from api_client import api
from components.modals import open_detalhes_atividade_modal, open_confirmacao_modal, show_snackbar


class AtividadesPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.flet_page = page
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = ft.padding.all(24)

        # Filtros
        self.filtro_termo = ""
        self.filtro_status = "Todos"
        self.filtro_prioridade = "Todas"
        self.filtro_prazo = "todos"

        self.content = self._build_view()

    def refresh(self):
        self.content = self._build_view()
        self.update()

    def _build_view(self):
        # Carregar atividades com filtros via API
        params = {}
        if self.filtro_termo:
            params["q"] = self.filtro_termo
        if self.filtro_status != "Todos":
            params["status"] = self.filtro_status
        if self.filtro_prioridade != "Todas":
            params["prioridade"] = self.filtro_prioridade
        if self.filtro_prazo != "todos":
            params["prazo"] = self.filtro_prazo

        atividades, err = api.get_atividades(params)
        atividades = atividades or []

        # Controles de Filtros
        txt_busca = ft.TextField(
            hint_text="Buscar por título ou descrição...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            value=self.filtro_termo,
            expand=True,
            dense=True,
        )
        def on_busca(e):
            self.filtro_termo = txt_busca.value.strip()
            self.refresh()
        txt_busca.on_submit = on_busca

        dd_status = ft.Dropdown(
            label="Status",
            options=[
                ft.dropdown.Option("Todos"),
                ft.dropdown.Option("A fazer"),
                ft.dropdown.Option("Em andamento"),
                ft.dropdown.Option("Em revisão"),
                ft.dropdown.Option("Concluído"),
            ],
            value=self.filtro_status,
            width=150,
            dense=True,
        )
        def on_status_change(e):
            self.filtro_status = dd_status.value
            self.refresh()
        dd_status.on_change = on_status_change

        dd_prio = ft.Dropdown(
            label="Prioridade",
            options=[
                ft.dropdown.Option("Todas"),
                ft.dropdown.Option("Baixa"),
                ft.dropdown.Option("Média"),
                ft.dropdown.Option("Alta"),
                ft.dropdown.Option("Urgente"),
            ],
            value=self.filtro_prioridade,
            width=150,
            dense=True,
        )
        def on_prio_change(e):
            self.filtro_prioridade = dd_prio.value
            self.refresh()
        dd_prio.on_change = on_prio_change

        dd_prazo = ft.Dropdown(
            label="Prazo",
            options=[
                ft.dropdown.Option("todos", "Todos"),
                ft.dropdown.Option("atrasadas", "Atrasadas"),
                ft.dropdown.Option("hoje", "Vencem Hoje"),
                ft.dropdown.Option("semana", "Próxima Semana"),
            ],
            value=self.filtro_prazo,
            width=160,
            dense=True,
        )
        def on_prazo_change(e):
            self.filtro_prazo = dd_prazo.value
            self.refresh()
        dd_prazo.on_change = on_prazo_change

        filters_row = ft.Row(
            controls=[txt_busca, dd_status, dd_prio, dd_prazo],
            spacing=10,
        )

        # Cabeçalho da Tabela / Lista
        header_row = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text("ATIVIDADE", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, expand=3),
                    ft.Text("QUADRO", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, expand=2),
                    ft.Text("VENCIMENTO", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, expand=2),
                    ft.Text("PRIORIDADE", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, expand=2),
                    ft.Text("STATUS", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, expand=2),
                    ft.Text("AÇÕES", size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, width=80),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
        )

        rows = []
        for a in atividades:
            aid = a["id"]
            prio = a.get("prioridade", "Média")
            p_style = PRIORITY_COLORS.get(prio, PRIORITY_COLORS["Média"])
            st = a.get("status", "A fazer")
            st_style = STATUS_COLORS.get(st, STATUS_COLORS["A fazer"])

            def on_excluir(e, atv_id=aid, atv_tit=a.get("titulo")):
                def confirmar(ev):
                    self.flet_page.pop_dialog()
                    api.delete_atividade(atv_id)
                    show_snackbar(self.flet_page, "Atividade removida.")
                    self.refresh()
                open_confirmacao_modal(self.flet_page, f"Excluir '{atv_tit}'?", "Essa operação removerá a atividade permanentemente.", confirmar)

            row_container = ft.Container(
                content=ft.Row(
                    controls=[
                        # Título e Categoria
                        ft.Column(
                            controls=[
                                ft.Text(a.get("titulo", ""), size=13, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                                ft.Text(a.get("categoria", {}).get("nome") or "Sem categoria", size=10, color=COLOR_TEXT_SECONDARY) if a.get("categoria") else ft.Container(),
                            ],
                            spacing=1,
                            expand=3,
                        ),
                        # Quadro
                        ft.Text(a.get("quadro_nome") or "Geral", size=12, color=COLOR_TEXT_SECONDARY, expand=2),
                        # Vencimento
                        ft.Text(a.get("data_vencimento") or "—", size=12, color=COLOR_TEXT_SECONDARY, expand=2),
                        # Prioridade
                        ft.Container(
                            content=ft.Text(prio, size=10, weight=ft.FontWeight.BOLD, color=p_style["text"]),
                            bgcolor=p_style["bg"],
                            border=ft.border.all(1, p_style["border"]),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            alignment=ft.alignment.center_left,
                            expand=2,
                        ),
                        # Status
                        ft.Container(
                            content=ft.Text(st, size=10, weight=ft.FontWeight.BOLD, color=st_style["text"]),
                            bgcolor=st_style["bg"],
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            alignment=ft.alignment.center_left,
                            expand=2,
                        ),
                        # Ações
                        ft.Row(
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY_OUTLINED,
                                    icon_size=16,
                                    icon_color=COLOR_TEXT_SECONDARY,
                                    tooltip="Ver/Editar Detalhes",
                                    on_click=lambda e, atv_id=aid: open_detalhes_atividade_modal(self.flet_page, atv_id, self.refresh)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                                    icon_size=16,
                                    icon_color=COLOR_DANGER,
                                    tooltip="Excluir Atividade",
                                    on_click=on_excluir
                                ),
                            ],
                            spacing=0,
                            width=80,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor=COLOR_SURFACE,
                border=ft.border.all(1, COLOR_BORDER),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=16, vertical=10),
                ink=True,
                on_click=lambda e, atv_id=aid: open_detalhes_atividade_modal(self.flet_page, atv_id, self.refresh)
            )
            rows.append(row_container)

        lista_content = ft.Column(
            controls=rows if rows else [
                ft.Container(
                    content=ft.Text("Nenhuma atividade encontrada com os filtros selecionados.", size=12, italic=True, color=COLOR_TEXT_SECONDARY),
                    padding=ft.padding.all(30),
                    alignment=ft.alignment.center,
                )
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return ft.Column(
            controls=[
                ft.Row([
                    ft.Text("Minhas Atividades", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ft.Text(f"{len(atividades)} resultado(s)", size=12, color=COLOR_TEXT_SECONDARY),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                filters_row,
                header_row,
                lista_content,
            ],
            spacing=14,
            expand=True,
        )
