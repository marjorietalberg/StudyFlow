from datetime import date
import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_SURFACE_ALT, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_BORDER, COLOR_DANGER, COLOR_WARNING, COLOR_SUCCESS,
    PRIORITY_COLORS
)
from api_client import api
from components.modals import (
    open_nova_atividade_modal, open_detalhes_atividade_modal,
    open_nova_lista_modal, open_confirmacao_modal, show_snackbar
)


class KanbanPage(ft.Container):
    def __init__(self, page: ft.Page, active_board_id: int = None):
        super().__init__()
        self.flet_page = page
        self.active_board_id = active_board_id
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = ft.padding.all(20)

        self.content = self._build_view()

    def set_board(self, board_id: int):
        self.active_board_id = board_id
        self.refresh()

    def refresh(self):
        self.content = self._build_view()
        self.update()

    def _build_card_item(self, atv, current_list_index: int, all_lists: list):
        aid = atv["id"]
        titulo = atv.get("titulo", "Atividade")
        prio = atv.get("prioridade", "Média")
        p_style = PRIORITY_COLORS.get(prio, PRIORITY_COLORS["Média"])
        venc = atv.get("data_vencimento")
        cat = atv.get("categoria")
        etiqs = atv.get("etiquetas") or []
        checklists = atv.get("checklists") or []

        # Indicador de prazo
        hoje_str = date.today().strftime("%Y-%m-%d")
        badge_venc_color = COLOR_TEXT_SECONDARY
        badge_venc_bg = COLOR_SURFACE_ALT

        if venc and atv.get("status") != "Concluído":
            if venc < hoje_str:
                badge_venc_color = COLOR_DANGER
                badge_venc_bg = "#FEE2E2"
            elif venc == hoje_str:
                badge_venc_color = COLOR_WARNING
                badge_venc_bg = "#FEF3C7"

        # Indicador de checklist
        total_ck = len(checklists)
        concl_ck = sum(1 for c in checklists if c.get("concluido"))

        # Botões de movimentação entre colunas (Trello-like move)
        btn_move_left = None
        if current_list_index > 0:
            target_list_id = all_lists[current_list_index - 1]["id"]
            def on_left(e, t_lid=target_list_id):
                api.patch_atividade_status(aid, {"lista_id": t_lid})
                self.refresh()
            btn_move_left = ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT_ROUNDED,
                icon_size=16,
                icon_color=COLOR_TEXT_SECONDARY,
                tooltip="Mover para coluna anterior",
                on_click=on_left
            )

        btn_move_right = None
        if current_list_index < len(all_lists) - 1:
            target_list_id = all_lists[current_list_index + 1]["id"]
            def on_right(e, t_lid=target_list_id):
                api.patch_atividade_status(aid, {"lista_id": t_lid})
                self.refresh()
            btn_move_right = ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT_ROUNDED,
                icon_size=16,
                icon_color=COLOR_TEXT_SECONDARY,
                tooltip="Mover para próxima coluna",
                on_click=on_right
            )

        # Chips de etiquetas
        etiq_chips = []
        for et in etiqs:
            etiq_chips.append(
                ft.Container(
                    content=ft.Text(et["nome"], size=9, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    bgcolor=et.get("cor", COLOR_PRIMARY),
                    border_radius=4,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                )
            )

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho do Cartão: Prioridade e Categoria
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(prio, size=10, weight=ft.FontWeight.BOLD, color=p_style["text"]),
                                bgcolor=p_style["bg"],
                                border=ft.border.all(1, p_style["border"]),
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            ),
                            ft.Container(
                                content=ft.Text(cat["nome"], size=10, weight=ft.FontWeight.W_500, color=cat.get("cor", COLOR_PRIMARY)),
                                bgcolor=ft.Colors.with_opacity(0.12, cat.get("cor", COLOR_PRIMARY)),
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            ) if cat else ft.Container(),
                        ],
                        spacing=6,
                    ),
                    # Título da Atividade
                    ft.Text(titulo, size=13, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                    # Etiquetas se houver
                    ft.Row(controls=etiq_chips, wrap=True, spacing=4) if etiq_chips else ft.Container(),
                    # Rodapé do Cartão: Checklist, Prazo e Ações
                    ft.Divider(color=COLOR_BORDER, height=8),
                    ft.Row(
                        controls=[
                            ft.Row([
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.CHECKLIST_ROUNDED, size=14, color=COLOR_PRIMARY),
                                        ft.Text(f"{concl_ck}/{total_ck}", size=10, color=COLOR_TEXT_SECONDARY),
                                    ], spacing=2),
                                ) if total_ck > 0 else ft.Container(),
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.CALENDAR_TODAY_ROUNDED, size=12, color=badge_venc_color),
                                        ft.Text(venc, size=10, weight=ft.FontWeight.W_500, color=badge_venc_color),
                                    ], spacing=2),
                                    bgcolor=badge_venc_bg,
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=4, vertical=2),
                                ) if venc else ft.Container(),
                            ], spacing=6),
                            ft.Row([
                                btn_move_left or ft.Container(width=16),
                                ft.IconButton(
                                    icon=ft.Icons.VISIBILITY_OUTLINED,
                                    icon_size=16,
                                    icon_color=COLOR_TEXT_SECONDARY,
                                    tooltip="Ver/Editar Detalhes",
                                    on_click=lambda e: open_detalhes_atividade_modal(self.flet_page, aid, self.refresh)
                                ),
                                btn_move_right or ft.Container(width=16),
                            ], spacing=0),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    )
                ],
                spacing=6,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=10,
            padding=ft.padding.all(12),
            ink=True,
            on_click=lambda e: open_detalhes_atividade_modal(self.flet_page, aid, self.refresh),
        )

    def _build_column(self, lista_data, list_index: int, all_lists: list):
        lid = lista_data["id"]
        nome_lista = lista_data["nome"]
        atividades = lista_data.get("atividades") or []
        count = len(atividades)

        # Botão excluir lista
        def on_excluir_lista(e):
            def confirmar(ev):
                self.flet_page.pop_dialog()
                api.delete_lista(lid)
                self.refresh()
            open_confirmacao_modal(
                self.flet_page,
                f"Excluir coluna '{nome_lista}'?",
                "Todas as atividades nesta coluna serão removidas.",
                confirmar
            )

        cards_controls = [
            self._build_card_item(a, list_index, all_lists)
            for a in atividades
        ]

        return ft.Container(
            content=ft.Column(
                controls=[
                    # Cabeçalho da Coluna Kanban
                    ft.Row(
                        controls=[
                            ft.Row([
                                ft.Text(nome_lista, size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                                ft.Container(
                                    content=ft.Text(str(count), size=11, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                                    bgcolor=COLOR_PRIMARY_LIGHT,
                                    border_radius=10,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                ),
                            ], spacing=8),
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.ADD_ROUNDED,
                                    icon_size=18,
                                    icon_color=COLOR_TEXT_SECONDARY,
                                    tooltip=f"Adicionar cartão em '{nome_lista}'",
                                    on_click=lambda e: open_nova_atividade_modal(self.flet_page, self.refresh, preselected_board_id=self.active_board_id, preselected_list_id=lid)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.MORE_HORIZ_ROUNDED,
                                    icon_size=18,
                                    icon_color=COLOR_TEXT_SECONDARY,
                                    tooltip="Opções da Coluna",
                                    on_click=on_excluir_lista,
                                ),
                            ], spacing=0),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(color=COLOR_BORDER, height=4),
                    # Lista de Cartões Rolável
                    ft.Column(
                        controls=cards_controls if cards_controls else [
                            ft.Container(
                                content=ft.Text("Nenhum cartão nesta lista.", size=11, italic=True, color=COLOR_TEXT_SECONDARY),
                                padding=ft.padding.symmetric(vertical=20),
                                alignment=ft.alignment.center,
                            )
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=10,
                        expand=True,
                    ),
                    # Botão rápido "+ Adicionar Cartão" no rodapé da coluna
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD_ROUNDED, size=16, color=COLOR_TEXT_SECONDARY),
                            ft.Text("Adicionar cartão", size=12, color=COLOR_TEXT_SECONDARY, weight=ft.FontWeight.W_500),
                        ], spacing=6),
                        padding=ft.padding.symmetric(vertical=8),
                        border_radius=8,
                        ink=True,
                        on_click=lambda e: open_nova_atividade_modal(self.flet_page, self.refresh, preselected_board_id=self.active_board_id, preselected_list_id=lid),
                    )
                ],
                spacing=8,
                expand=True,
            ),
            width=290,
            bgcolor=COLOR_SURFACE_ALT,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(12),
        )

    def _build_view(self):
        quadros, _ = api.get_quadros()
        quadros = quadros or []

        if not quadros:
            return ft.Column([
                ft.Text("Nenhum quadro cadastrado.", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                ft.Text("Crie seu primeiro quadro para acessar o Kanban visual.", size=13, color=COLOR_TEXT_SECONDARY),
            ])

        # Se active_board_id não estiver setado, pega o primeiro
        if not self.active_board_id or not any(q["id"] == self.active_board_id for q in quadros):
            self.active_board_id = quadros[0]["id"]

        quadro_atual, err = api.get_quadro(self.active_board_id)
        if err or not quadro_atual:
            return ft.Text(f"Erro ao carregar quadro: {err}", color=COLOR_DANGER)

        listas = quadro_atual.get("listas") or []

        # Dropdown para alternar quadro
        dd_quadros = ft.Dropdown(
            options=[ft.dropdown.Option(str(q["id"]), q["nome"]) for q in quadros],
            value=str(self.active_board_id),
            width=240,
            dense=True,
        )
        def on_change_board(e):
            self.active_board_id = int(dd_quadros.value)
            self.refresh()
        dd_quadros.on_change = on_change_board

        # Barra Superior do Kanban
        toolbar = ft.Row(
            controls=[
                ft.Row([
                    ft.Text("Quadro:", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY),
                    dd_quadros,
                    ft.Container(
                        width=14,
                        height=14,
                        border_radius=7,
                        bgcolor=quadro_atual.get("cor", COLOR_PRIMARY),
                        tooltip="Cor identificadora do quadro"
                    ),
                ], spacing=10),
                ft.Row([
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.VIEW_COLUMN_ROUNDED, size=16, color=COLOR_PRIMARY),
                            ft.Text("Nova Coluna", size=12, weight=ft.FontWeight.W_600, color=COLOR_PRIMARY),
                        ], spacing=6),
                        bgcolor=COLOR_PRIMARY_LIGHT,
                        on_click=lambda e: open_nova_lista_modal(self.flet_page, self.active_board_id, self.refresh),
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD_ROUNDED, size=16, color=ft.Colors.WHITE),
                            ft.Text("Adicionar Cartão", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                        ], spacing=6),
                        bgcolor=COLOR_PRIMARY,
                        on_click=lambda e: open_nova_atividade_modal(self.flet_page, self.refresh, preselected_board_id=self.active_board_id),
                    ),
                ], spacing=10),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Colunas horizontais
        columns_controls = [
            self._build_column(l, idx, listas)
            for idx, l in enumerate(listas)
        ]

        board_scroll = ft.Row(
            controls=columns_controls,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return ft.Column(
            controls=[
                toolbar,
                ft.Divider(color=COLOR_BORDER, height=8),
                board_scroll,
            ],
            spacing=12,
            expand=True,
        )
