import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER,
    COLOR_SUCCESS, PRIORITY_COLORS
)
from api_client import api
from components.modals import open_detalhes_atividade_modal, show_snackbar


class ConcluidasPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.flet_page = page
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = ft.padding.all(24)

        self.content = self._build_view()

    def refresh(self):
        self.content = self._build_view()
        self.update()

    def _build_view(self):
        # Filtrar apenas atividades com status Concluído
        atividades, _ = api.get_atividades({"status": "Concluído"})
        atividades = atividades or []

        header = ft.Row(
            controls=[
                ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color=COLOR_SUCCESS, size=24),
                        ft.Text("Histórico de Atividades Concluídas", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ], spacing=10),
                    ft.Text("Consulte o histórico de conquistas e reabra atividades quando necessário.", size=12, color=COLOR_TEXT_SECONDARY),
                ], spacing=2),
                ft.Container(
                    content=ft.Text(f"{len(atividades)} Finalizada(s)", size=12, weight=ft.FontWeight.BOLD, color=COLOR_SUCCESS),
                    bgcolor="#D1FAE5",
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        rows = []
        for a in atividades:
            aid = a["id"]
            prio = a.get("prioridade", "Média")
            p_style = PRIORITY_COLORS.get(prio, PRIORITY_COLORS["Média"])
            dt_conc = a.get("data_conclusao") or a.get("data_vencimento") or "—"
            if isinstance(dt_conc, str) and "T" in dt_conc:
                dt_conc = dt_conc.split("T")[0]

            def on_reabrir(e, atv_id=aid, atv_tit=a.get("titulo")):
                # Reabre mudando status para 'Em andamento'
                res, err = api.patch_atividade_status(atv_id, {"status": "Em andamento"})
                if err:
                    show_snackbar(self.flet_page, f"Erro ao reabrir: {err}", is_error=True)
                else:
                    show_snackbar(self.flet_page, f"Atividade '{atv_tit}' reaberta com sucesso!")
                    self.refresh()

            row_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Row([
                            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=COLOR_SUCCESS, size=20),
                            ft.Column([
                                ft.Text(a.get("titulo", ""), size=14, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                                ft.Row([
                                    ft.Text(f"Quadro: {a.get('quadro_nome') or 'Geral'}", size=11, color=COLOR_PRIMARY),
                                    ft.Text(f"• Categoria: {a.get('categoria', {}).get('nome') or 'Geral'}", size=11, color=COLOR_TEXT_SECONDARY) if a.get("categoria") else ft.Container(),
                                    ft.Text(f"• Concluída em: {dt_conc}", size=11, color=COLOR_TEXT_SECONDARY),
                                ], spacing=6),
                            ], spacing=2),
                        ], spacing=12, expand=True),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(prio, size=10, weight=ft.FontWeight.BOLD, color=p_style["text"]),
                                bgcolor=p_style["bg"],
                                border=ft.border.all(1, p_style["border"]),
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            ),
                            ft.ElevatedButton(
                                content=ft.Row([
                                    ft.Icon(ft.Icons.REPLAY_ROUNDED, size=14, color=COLOR_PRIMARY),
                                    ft.Text("Reabrir Atividade", size=11, weight=ft.FontWeight.W_600, color=COLOR_PRIMARY),
                                ], spacing=4),
                                bgcolor=COLOR_PRIMARY_LIGHT,
                                on_click=on_reabrir,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY_OUTLINED,
                                icon_size=18,
                                icon_color=COLOR_TEXT_SECONDARY,
                                tooltip="Visualizar Detalhes",
                                on_click=lambda e, atv_id=aid: open_detalhes_atividade_modal(self.flet_page, atv_id, self.refresh),
                            )
                        ], spacing=10),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=COLOR_SURFACE,
                border=ft.border.all(1, COLOR_BORDER),
                border_radius=10,
                padding=ft.padding.all(14),
            )
            rows.append(row_card)

        lista_content = ft.Column(
            controls=rows if rows else [
                ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.Icons.DONE_ALL_ROUNDED, size=40, color=COLOR_TEXT_SECONDARY),
                        ft.Text("Nenhuma atividade concluída ainda.", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                        ft.Text("Mova cartões para a coluna 'Concluído' no Kanban para registrá-las aqui.", size=11, color=COLOR_TEXT_SECONDARY),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6),
                    padding=ft.padding.all(40),
                    alignment=ft.alignment.center,
                )
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        return ft.Column(
            controls=[
                header,
                ft.Divider(color=COLOR_BORDER, height=12),
                lista_content,
            ],
            spacing=14,
            expand=True,
        )
