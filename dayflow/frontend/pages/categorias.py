import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_LIGHT, COLOR_BG, COLOR_SURFACE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_BORDER,
    COLOR_DANGER, PALETTE_PRESETS
)
from api_client import api
from components.modals import open_confirmacao_modal, show_snackbar


class CategoriasPage(ft.Container):
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
        categorias, _ = api.get_categorias()
        categorias = categorias or []

        etiquetas, _ = api.get_etiquetas()
        etiquetas = etiquetas or []

        # ==========================================
        # SEÇÃO 1: CATEGORIAS
        # ==========================================
        txt_nova_cat = ft.TextField(hint_text="Nome da nova categoria...", expand=True, dense=True)
        cat_cor_ref = ft.Ref[str]()
        cat_cor_ref.current = PALETTE_PRESETS[0]

        def on_cadastrar_cat(e):
            nome = txt_nova_cat.value.strip() if txt_nova_cat.value else ""
            if not nome:
                show_snackbar(self.flet_page, "Informe o nome da categoria.", is_error=True)
                return
            res, err = api.create_categoria({"nome": nome, "cor": cat_cor_ref.current})
            if err:
                show_snackbar(self.flet_page, f"Erro: {err}", is_error=True)
            else:
                show_snackbar(self.flet_page, f"Categoria '{nome}' criada com sucesso!")
                txt_nova_cat.value = ""
                self.refresh()

        lista_cat_controls = []
        for c in categorias:
            cid = c["id"]
            cnome = c["nome"]
            ccor = c.get("cor", COLOR_PRIMARY)

            def on_excluir_cat(e, cat_id=cid, cat_nome=cnome):
                def confirmar(ev):
                    self.flet_page.pop_dialog()
                    api.delete_categoria(cat_id)
                    show_snackbar(self.flet_page, f"Categoria '{cat_nome}' removida.")
                    self.refresh()
                open_confirmacao_modal(self.flet_page, f"Excluir categoria '{cat_nome}'?", "As atividades vinculadas manterão seus dados, mas ficarão sem categoria.", confirmar)

            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Row([
                            ft.Container(width=16, height=16, border_radius=8, bgcolor=ccor),
                            ft.Text(cnome, size=13, weight=ft.FontWeight.W_600, color=COLOR_TEXT_PRIMARY),
                        ], spacing=10),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_size=16, icon_color=COLOR_DANGER, tooltip="Excluir", on_click=on_excluir_cat),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=COLOR_SURFACE,
                border=ft.border.all(1, COLOR_BORDER),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
            )
            lista_cat_controls.append(item)

        painel_categorias = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.CATEGORY_ROUNDED, color=COLOR_PRIMARY, size=20),
                        ft.Text("Categorias Principais", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ], spacing=8),
                    ft.Text("Classifique suas atividades em grandes áreas (Estudos, Trabalho, Pessoal, etc.)", size=11, color=COLOR_TEXT_SECONDARY),
                    ft.Divider(color=COLOR_BORDER, height=8),
                    ft.Row([
                        txt_nova_cat,
                        ft.ElevatedButton("Adicionar", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=on_cadastrar_cat),
                    ], spacing=8),
                    ft.Column(
                        controls=lista_cat_controls if lista_cat_controls else [
                            ft.Text("Nenhuma categoria cadastrada.", size=12, italic=True, color=COLOR_TEXT_SECONDARY)
                        ],
                        spacing=6,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(20),
            expand=1,
        )

        # ==========================================
        # SEÇÃO 2: ETIQUETAS (TAGS)
        # ==========================================
        txt_nova_etiq = ft.TextField(hint_text="Nome da nova etiqueta...", expand=True, dense=True)
        etiq_cor_ref = ft.Ref[str]()
        etiq_cor_ref.current = PALETTE_PRESETS[1]

        def on_cadastrar_etiq(e):
            nome = txt_nova_etiq.value.strip() if txt_nova_etiq.value else ""
            if not nome:
                show_snackbar(self.flet_page, "Informe o nome da etiqueta.", is_error=True)
                return
            res, err = api.create_etiqueta({"nome": nome, "cor": etiq_cor_ref.current})
            if err:
                show_snackbar(self.flet_page, f"Erro: {err}", is_error=True)
            else:
                show_snackbar(self.flet_page, f"Etiqueta '{nome}' criada com sucesso!")
                txt_nova_etiq.value = ""
                self.refresh()

        lista_etiq_controls = []
        for et in etiquetas:
            eid = et["id"]
            enome = et["nome"]
            ecor = et.get("cor", COLOR_PRIMARY)

            def on_excluir_etiq(e, etiq_id=eid, etiq_nome=enome):
                def confirmar(ev):
                    self.flet_page.pop_dialog()
                    api.delete_etiqueta(etiq_id)
                    show_snackbar(self.flet_page, f"Etiqueta '{etiq_nome}' removida.")
                    self.refresh()
                open_confirmacao_modal(self.flet_page, f"Excluir etiqueta '{etiq_nome}'?", "A etiqueta será desvinculada dos cartões.", confirmar)

            item = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Row([
                            ft.Container(
                                content=ft.Text(enome, size=11, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                bgcolor=ecor,
                                border_radius=6,
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            ),
                        ], spacing=10),
                        ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_size=16, icon_color=COLOR_DANGER, tooltip="Excluir", on_click=on_excluir_etiq),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=COLOR_SURFACE,
                border=ft.border.all(1, COLOR_BORDER),
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=12, vertical=8),
            )
            lista_etiq_controls.append(item)

        painel_etiquetas = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([
                        ft.Icon(ft.Icons.LABEL_ROUNDED, color=COLOR_PRIMARY, size=20),
                        ft.Text("Etiquetas de Identificação (Tags)", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                    ], spacing=8),
                    ft.Text("Rotule seus cartões com tags específicas (ex: Backend, Design, Urgente, Revisão)", size=11, color=COLOR_TEXT_SECONDARY),
                    ft.Divider(color=COLOR_BORDER, height=8),
                    ft.Row([
                        txt_nova_etiq,
                        ft.ElevatedButton("Adicionar", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=on_cadastrar_etiq),
                    ], spacing=8),
                    ft.Column(
                        controls=lista_etiq_controls if lista_etiq_controls else [
                            ft.Text("Nenhuma etiqueta cadastrada.", size=12, italic=True, color=COLOR_TEXT_SECONDARY)
                        ],
                        spacing=6,
                        scroll=ft.ScrollMode.AUTO,
                    ),
                ],
                spacing=12,
            ),
            bgcolor=COLOR_SURFACE,
            border=ft.border.all(1, COLOR_BORDER),
            border_radius=12,
            padding=ft.padding.all(20),
            expand=1,
        )

        return ft.Column(
            controls=[
                ft.Row([
                    ft.Column([
                        ft.Text("Gerenciamento de Categorias & Etiquetas", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_PRIMARY),
                        ft.Text("Personalize como suas atividades são classificadas e identificadas visualmente nos quadros.", size=12, color=COLOR_TEXT_SECONDARY),
                    ], spacing=2),
                ]),
                ft.Row([painel_categorias, painel_etiquetas], spacing=20, expand=True),
            ],
            spacing=16,
            expand=True,
        )
