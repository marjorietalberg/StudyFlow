import os
import sys

# Adicionar diretório atual e pai ao sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import flet as ft
from theme import COLOR_BG, COLOR_PRIMARY
from components.sidebar import Sidebar
from components.header import Header
from components.modals import open_nova_atividade_modal

from pages.dashboard import DashboardPage
from pages.quadros import QuadrosPage
from pages.kanban import KanbanPage
from pages.atividades import AtividadesPage
from pages.calendario import CalendarioPage
from pages.categorias import CategoriasPage
from pages.concluidas import ConcluidasPage


PAGE_INFO = {
    "dashboard": ("Dashboard Geral", "Métricas em tempo real, entregas próximas e indicadores de produtividade"),
    "quadros": ("Meus Quadros", "Gerenciamento de projetos, estudos e fluxos de trabalho"),
    "kanban": ("Quadro Kanban Visual", "Fluxo de cartões com colunas A Fazer, Em Andamento, Em Revisão e Concluído"),
    "atividades": ("Minhas Atividades", "Consulta unificada com filtros avançados e ordenação por vencimento"),
    "calendario": ("Agenda & Calendário", "Visualização mensal e acompanhamento preditivo de datas de entrega"),
    "categorias": ("Categorias & Etiquetas", "Classificação estruturada de atividades e tags visuais"),
    "concluidas": ("Histórico de Concluídas", "Registro e auditoria de atividades finalizadas"),
}


def main(page: ft.Page):
    page.title = "DayFlow — Gerenciador Inteligente de Atividades"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = COLOR_BG
    page.padding = 0
    page.window.width = 1360
    page.window.height = 840
    page.window.min_width = 1000
    page.window.min_height = 650

    # Estado de navegação
    current_page_id = ["dashboard"]
    active_board_id = [None]

    # Container de conteúdo central
    content_area = ft.Container(expand=True, bgcolor=COLOR_BG)

    # Função para renderizar página atual
    def carregar_pagina(page_id: str):
        current_page_id[0] = page_id
        title, subtitle = PAGE_INFO.get(page_id, ("DayFlow", "Gerenciador Visual"))
        header.update_header(title, subtitle)
        sidebar.set_current_page(page_id)

        if page_id == "dashboard":
            content_area.content = DashboardPage(
                page=page,
                on_navigate_kanban=lambda: carregar_pagina("kanban")
            )
        elif page_id == "quadros":
            def on_open_board(qid):
                active_board_id[0] = qid
                carregar_pagina("kanban")
            content_area.content = QuadrosPage(page=page, on_open_board=on_open_board)
        elif page_id == "kanban":
            content_area.content = KanbanPage(page=page, active_board_id=active_board_id[0])
        elif page_id == "atividades":
            content_area.content = AtividadesPage(page=page)
        elif page_id == "calendario":
            content_area.content = CalendarioPage(page=page)
        elif page_id == "categorias":
            content_area.content = CategoriasPage(page=page)
        elif page_id == "concluidas":
            content_area.content = ConcluidasPage(page=page)

        page.update()

    def on_refresh_current():
        if hasattr(content_area.content, "refresh"):
            content_area.content.refresh()

    def on_new_task_btn():
        open_nova_atividade_modal(page, on_refresh_current, preselected_board_id=active_board_id[0])

    # Instanciação dos componentes globais
    sidebar = Sidebar(on_page_change=carregar_pagina, current_page=current_page_id[0])
    header = Header(
        title=PAGE_INFO["dashboard"][0],
        subtitle=PAGE_INFO["dashboard"][1],
        on_new_task=on_new_task_btn,
        on_refresh=on_refresh_current,
    )

    # Layout Principal: Sidebar à esquerda + Coluna com Header e Content Area
    main_layout = ft.Row(
        controls=[
            sidebar,
            ft.Column(
                controls=[
                    header,
                    content_area,
                ],
                spacing=0,
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )

    page.add(main_layout)
    carregar_pagina("dashboard")


if __name__ == "__main__":
    port = int(os.environ.get("DAYFLOW_FRONTEND_PORT", 8550))
    print(f"🚀 Iniciando Frontend Flet do DayFlow em http://127.0.0.1:{port}")
    ft.run(main, view=ft.AppView.WEB_BROWSER, port=port)
