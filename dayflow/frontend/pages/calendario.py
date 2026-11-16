import calendar
from datetime import date, datetime, timedelta
import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_SURFACE_ALT, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_BORDER, COLOR_DANGER, COLOR_WARNING, COLOR_SUCCESS,
    PRIORITY_COLORS
)
from api_client import api
from components.modals import open_nova_atividade_modal, open_detalhes_atividade_modal


class CalendarioPage(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.flet_page = page
        self.expand = True
        self.bgcolor = COLOR_BG
        self.padding = ft.padding.all(24)

        hoje = date.today()
        self.current_year = hoje.year
        self.current_month = hoje.month
        self.selected_date = hoje.strftime("%Y-%m-%d")

        self.content = self._build_view()

    def refresh(self):
        self.content = self._build_view()
        self.update()

    def _prev_month(self, e):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh()

    def _next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh()

    def _select_date(self, data_str: str):
        self.selected_date = data_str
        self.refresh()

    def _build_view(self):
        atividades, _ = api.get_atividades()
        atividades = atividades or []

        # Agrupar atividades por data_vencimento
        atividades_por_data = {}
        for a in atividades:
            v = a.get("data_vencimento")
            if v:
                atividades_por_data.setdefault(v, []).append(a)

        # Cabeçalho do mês e navegação
        nomes_meses = [
            "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        mes_nome = nomes_meses[self.current_month]

        header_nav = ft.Row(
            controls=[
                ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_MONTH_ROUNDED, color=COLOR_PRIMARY, size=24),
                    ft.Text(f"{mes_nome} {self.current_year}", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                ], spacing=10),
                ft.Row([
                    ft.IconButton(ft.Icons.CHEVRON_LEFT_ROUNDED, on_click=self._prev_month, tooltip="Mês Anterior"),
                    ft.ElevatedButton(
                        "Hoje",
                        bgcolor=COLOR_PRIMARY_LIGHT,
                        color=COLOR_PRIMARY,
                        on_click=lambda e: (
                            setattr(self, "current_year", date.today().year),
                            setattr(self, "current_month", date.today().month),
                            self._select_date(date.today().strftime("%Y-%m-%d"))
                        )
                    ),
                    ft.IconButton(ft.Icons.CHEVRON_RIGHT_ROUNDED, on_click=self._next_month, tooltip="Próximo Mês"),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.ADD_ROUNDED, size=16, color=ft.Colors.WHITE),
                            ft.Text("Nova Atividade Nesta Data", size=12, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE),
                        ], spacing=6),
                        bgcolor=COLOR_PRIMARY,
                        on_click=lambda e: open_nova_atividade_modal(self.flet_page, self.refresh, preselected_date=self.selected_date),
                    ),
                ], spacing=8),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Grade do Calendário Mensal
        cal = calendar.monthcalendar(self.current_year, self.current_month)
        dias_semana = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

        header_dias = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(d, size=11, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY, text_align=ft.TextAlign.CENTER),
                    expand=True,
                    padding=ft.padding.symmetric(vertical=6),
                ) for d in dias_semana
            ],
            spacing=4,
        )

        hoje_str = date.today().strftime("%Y-%m-%d")

        semanas_controls = []
        for semana in cal:
            dias_row = []
            for d in semana:
                if d == 0:
                    dias_row.append(ft.Container(expand=True, height=72, bgcolor=COLOR_SURFACE_ALT, border_radius=6))
                else:
                    data_str = f"{self.current_year:04d}-{self.current_month:02d}-{d:02d}"
                    is_today = (data_str == hoje_str)
                    is_selected = (data_str == self.selected_date)
                    atvs_dia = atividades_por_data.get(data_str, [])
                    qtd = len(atvs_dia)

                    bg_cor = COLOR_PRIMARY_LIGHT if is_selected else (COLOR_SURFACE if not is_today else "#F3E8FF")
                    border_cor = COLOR_PRIMARY if (is_selected or is_today) else COLOR_BORDER

                    def on_click_dia(e, ds=data_str):
                        self._select_date(ds)

                    badges = []
                    if qtd > 0:
                        badges.append(
                            ft.Container(
                                content=ft.Text(f"{qtd} tarefa(s)", size=9, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARY),
                                bgcolor=COLOR_PRIMARY_LIGHT,
                                border_radius=4,
                                padding=ft.padding.symmetric(horizontal=4, vertical=1),
                            )
                        )

                    day_box = ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Row([
                                    ft.Text(str(d), size=12, weight=ft.FontWeight.BOLD if is_today else ft.FontWeight.W_500, color=COLOR_PRIMARY if is_today else COLOR_TEXT_PRIMARY),
                                    ft.Container(
                                        width=6, height=6, border_radius=3, bgcolor=COLOR_PRIMARY
                                    ) if is_today else ft.Container(),
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Column(controls=badges, spacing=2),
                            ],
                            spacing=4,
                        ),
                        bgcolor=bg_cor,
                        border=ft.border.all(1, border_cor),
                        border_radius=8,
                        padding=ft.padding.all(6),
                        height=72,
                        expand=True,
                        ink=True,
                        on_click=on_click_dia,
                    )
                    dias_row.append(day_box)
            semanas_controls.append(ft.Row(controls=dias_row, spacing=4))

        grade_calendario = ft.Container(
            content=ft.Column(
                controls=[header_dias] + semanas_controls,
                spacing=4,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(16),
            expand=3,
        )

        # Painel Lateral: Atividades da Data Selecionada
        atvs_selecionadas = atividades_por_data.get(self.selected_date, [])
        data_sel_obj = datetime.strptime(self.selected_date, "%Y-%m-%d")
        data_sel_formatada = data_sel_obj.strftime("%d de %B de %Y")

        itens_painel = []
        for a in atvs_selecionadas:
            prio = a.get("prioridade", "Média")
            p_style = PRIORITY_COLORS.get(prio, PRIORITY_COLORS["Média"])
            aid = a["id"]

            itens_painel.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row([
                                ft.Text(a.get("titulo", ""), size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY, expand=True),
                                ft.Container(
                                    content=ft.Text(prio, size=9, weight=ft.FontWeight.BOLD, color=p_style["text"]),
                                    bgcolor=p_style["bg"],
                                    border_radius=4,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                )
                            ]),
                            ft.Text(a.get("descricao") or "Sem descrição", size=11, color=COLOR_TEXT_SECONDARY, max_lines=2),
                            ft.Row([
                                ft.Text(f"Status: {a.get('status')}", size=10, weight=ft.FontWeight.W_500, color=COLOR_PRIMARY),
                                ft.Text(f"Quadro: {a.get('quadro_nome') or 'Geral'}", size=10, color=COLOR_TEXT_SECONDARY),
                            ], spacing=8),
                        ],
                        spacing=4,
                    ),
                    bgcolor=COLOR_BG,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=8,
                    padding=ft.padding.all(10),
                    ink=True,
                    on_click=lambda e, atv_id=aid: open_detalhes_atividade_modal(self.flet_page, atv_id, self.refresh),
                )
            )

        painel_detalhes_dia = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.EVENT_AVAILABLE_ROUNDED, color=COLOR_PRIMARY, size=18),
                        ft.Text(f"Tarefas para {data_sel_formatada}", size=13, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ], spacing=6),
                    ft.Divider(color=COLOR_BORDER, height=8),
                    ft.Column(
                        controls=itens_painel if itens_painel else [
                            ft.Container(
                                content=ft.Text("Nenhuma tarefa com vencimento nesta data.", size=12, italic=True, color=COLOR_TEXT_SECONDARY),
                                padding=ft.padding.symmetric(vertical=30),
                                alignment=ft.alignment.center,
                            )
                        ],
                        scroll=ft.ScrollMode.AUTO,
                        spacing=8,
                        expand=True,
                    ),
                ],
                spacing=8,
                expand=True,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(16),
            expand=2,
        )

        corpo_calendario = ft.Row(
            controls=[grade_calendario, painel_detalhes_dia],
            spacing=16,
            expand=True,
        )

        return ft.Column(
            controls=[
                header_nav,
                corpo_calendario,
            ],
            spacing=16,
            expand=True,
        )
