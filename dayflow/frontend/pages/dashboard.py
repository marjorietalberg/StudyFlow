from datetime import date
import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER,
    COLOR_SUCCESS, COLOR_WARNING, COLOR_DANGER, COLOR_INFO,
    PRIORITY_COLORS, STATUS_COLORS
)
from api_client import api
from components.modals import open_detalhes_atividade_modal, show_snackbar


class DashboardPage(ft.Container):
    def __init__(self, page: ft.Page, on_navigate_kanban=None):
        super().__init__()
        self.flet_page = page
        self.on_navigate_kanban = on_navigate_kanban
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = ft.padding.all(24)

        self.content = self._build_view()

    def refresh(self):
        self.content = self._build_view()
        self.update()

    def _build_kpi_card(self, title: str, value: str, icon_name, icon_color, subtitle: str = ""):
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(title, size=12, weight=ft.FontWeight.W_500, color=COLOR_TEXT_SECONDARY),
                            ft.Container(
                                content=ft.Icon(icon_name, size=18, color=icon_color),
                                bgcolor=ft.Colors.with_opacity(0.12, icon_color),
                                border_radius=6,
                                padding=ft.padding.all(6),
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(value, size=24, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ft.Text(subtitle, size=11, color=COLOR_TEXT_SECONDARY) if subtitle else ft.Container(),
                ],
                spacing=4,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(16),
            expand=True,
        )

    def _build_view(self):
        stats, err = api.get_dashboard_stats()
        if err or not stats:
            return ft.Column([
                ft.Text("Erro ao carregar métricas do Dashboard.", color=COLOR_DANGER, size=14),
                ft.Text(err or "Verifique o backend.", color=COLOR_TEXT_SECONDARY, size=12),
                ft.ElevatedButton("Tentar Novamente", on_click=lambda e: self.refresh()),
            ])

        hoje_extenso = date.today().strftime("%d de %B de %Y")

        # Saudação e Cabeçalho do Dashboard
        banner = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Row([
                                ft.Text("Olá! Bem-vindo ao DayFlow", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                                ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=COLOR_PRIMARY, size=20),
                            ], spacing=8),
                            ft.Text(f"Hoje é {hoje_extenso} • Visão executiva e acompanhamento em tempo real.", size=12, color=COLOR_TEXT_SECONDARY),
                        ],
                        spacing=4,
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.VIEW_KANBAN_ROUNDED, size=16, color=ft.Colors.WHITE),
                            ft.Text("Abrir Quadro Kanban", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                        ], spacing=6),
                        bgcolor=COLOR_PRIMARY,
                        on_click=lambda e: self.on_navigate_kanban() if self.on_navigate_kanban else None,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=16),
        )

        # 1ª Linha de KPIs Principais
        total = stats.get("total_atividades", 0)
        concluidas = stats.get("atividades_concluidas", 0)
        pendentes = stats.get("atividades_pendentes", 0)
        andamento = stats.get("atividades_em_andamento", 0)
        revisao = stats.get("atividades_em_revisao", 0)
        atrasadas = stats.get("atividades_atrasadas", 0)
        hoje_cnt = stats.get("atividades_hoje", 0)
        taxa = stats.get("taxa_conclusao_percentual", 0.0)

        kpis_row1 = ft.Row(
            controls=[
                self._build_kpi_card("Total de Atividades", str(total), ft.Icons.FORMAT_LIST_BULLETED_ROUNDED, COLOR_PRIMARY, "Cadastradas nos quadros"),
                self._build_kpi_card("A Fazer", str(pendentes), ft.Icons.RADIO_BUTTON_UNCHECKED_ROUNDED, COLOR_TEXT_SECONDARY, "Aguardando início"),
                self._build_kpi_card("Em Andamento", str(andamento), ft.Icons.PLAY_CIRCLE_OUTLINE_ROUNDED, COLOR_INFO, "Sendo executadas"),
                self._build_kpi_card("Em Revisão", str(revisao), ft.Icons.RATE_REVIEW_ROUNDED, COLOR_WARNING, "Aguardando validação"),
                self._build_kpi_card("Concluídas", str(concluidas), ft.Icons.CHECK_CIRCLE_ROUNDED, COLOR_SUCCESS, f"{taxa}% do total"),
            ],
            spacing=14,
        )

        # 2ª Linha de Alertas e Barra de Progresso Geral
        progress_val = (taxa / 100.0) if total > 0 else 0.0
        progresso_card = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Progresso Geral das Atividades", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                            ft.Text(f"{concluidas}/{total} finalizadas ({taxa}%)", size=12, weight=ft.FontWeight.W_600, color=COLOR_PRIMARY),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.ProgressBar(value=progress_val, color=COLOR_PRIMARY, bgcolor=COLOR_PRIMARY_LIGHT, height=8),
                ],
                spacing=8,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(16),
            expand=2,
        )

        alerta_atrasadas_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.WARNING_ROUNDED, color=COLOR_DANGER, size=24),
                        bgcolor=ft.Colors.with_opacity(0.12, COLOR_DANGER),
                        border_radius=8,
                        padding=ft.padding.all(8),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"{atrasadas} Atividades Atrasadas", size=14, weight=ft.FontWeight.BOLD, color=COLOR_DANGER),
                            ft.Text("Prazos expirados que requerem atenção imediata", size=11, color=COLOR_TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(14),
            expand=1,
        )

        alerta_hoje_card = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Icon(ft.Icons.TODAY_ROUNDED, color=COLOR_WARNING, size=24),
                        bgcolor=ft.Colors.with_opacity(0.12, COLOR_WARNING),
                        border_radius=8,
                        padding=ft.padding.all(8),
                    ),
                    ft.Column(
                        controls=[
                            ft.Text(f"{hoje_cnt} Vencem Hoje", size=14, weight=ft.FontWeight.BOLD, color=COLOR_WARNING),
                            ft.Text("Compromissos agendados para este dia", size=11, color=COLOR_TEXT_SECONDARY),
                        ],
                        spacing=2,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(14),
            expand=1,
        )

        kpis_row2 = ft.Row(
            controls=[progresso_card, alerta_atrasadas_card, alerta_hoje_card],
            spacing=14,
        )

        # Seção Central Dividida: Próximas Entregas e Atividades Recentes
        proximas_list = stats.get("proximas_entregas", [])
        recentes_list = stats.get("atividades_recentes", [])

        def render_task_mini_card(a):
            prio = a.get("prioridade", "Média")
            p_style = PRIORITY_COLORS.get(prio, PRIORITY_COLORS["Média"])

            return ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Column(
                            controls=[
                                ft.Text(a.get("titulo", ""), size=13, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Row([
                                    ft.Text(f"📅 {a.get('data_vencimento') or 'Sem prazo'}", size=11, color=COLOR_TEXT_SECONDARY),
                                    ft.Text(f"• {a.get('quadro_nome') or 'Quadro'}", size=11, color=COLOR_PRIMARY),
                                ], spacing=6),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.Container(
                            content=ft.Text(prio, size=10, weight=ft.FontWeight.BOLD, color=p_style["text"]),
                            bgcolor=p_style["bg"],
                            border=ft.border.all(1, p_style["border"]),
                            border_radius=6,
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=COLOR_BG,
                border=ft.border.all(1, COLOR_BORDER),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
                ink=True,
                on_click=lambda e, aid=a["id"]: open_detalhes_atividade_modal(self.flet_page, aid, self.refresh),
            )

        col_proximas = ft.Column(
            controls=[
                render_task_mini_card(a) for a in proximas_list
            ] if proximas_list else [ft.Text("Nenhuma entrega pendente para os próximos dias.", size=12, italic=True, color=COLOR_TEXT_SECONDARY)],
            spacing=8,
        )

        col_recentes = ft.Column(
            controls=[
                render_task_mini_card(a) for a in recentes_list
            ] if recentes_list else [ft.Text("Nenhuma atividade cadastrada recentemente.", size=12, italic=True, color=COLOR_TEXT_SECONDARY)],
            spacing=8,
        )

        painel_duplo = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, color=COLOR_PRIMARY, size=18),
                                ft.Text("Próximas Entregas & Prazos", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                            ], spacing=8),
                            col_proximas,
                        ],
                        spacing=12,
                    ),
                    bgcolor=COLOR_SURFACE,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=12,
                    padding=ft.padding.all(18),
                    expand=1,
                ),
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Icon(ft.Icons.HISTORY_ROUNDED, color=COLOR_PRIMARY, size=18),
                                ft.Text("Atividades Recentes", size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                            ], spacing=8),
                            col_recentes,
                        ],
                        spacing=12,
                    ),
                    bgcolor=COLOR_SURFACE,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=12,
                    padding=ft.padding.all(18),
                    expand=1,
                ),
            ],
            spacing=14,
        )

        return ft.Column(
            controls=[
                banner,
                kpis_row1,
                kpis_row2,
                ft.Container(height=8),
                painel_duplo,
            ],
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
