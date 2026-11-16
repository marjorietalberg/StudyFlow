from datetime import date
import flet as ft
from theme import (
    COLOR_PRIMARY, COLOR_SURFACE, COLOR_BORDER, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, COLOR_DANGER, PALETTE_PRESETS, PRIORITY_COLORS
)
from api_client import api


def show_snackbar(page: ft.Page, message: str, is_error: bool = False):
    """Exibe um aviso elegante na tela."""
    sb = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE, size=13),
        bgcolor=COLOR_DANGER if is_error else COLOR_PRIMARY,
    )
    page.show_dialog(sb)
    page.update()


def open_nova_atividade_modal(page: ft.Page, on_success_callback, preselected_board_id=None, preselected_list_id=None, preselected_date=None):
    """Abre modal elegante para cadastrar nova atividade conectada à API."""
    quadros, _ = api.get_quadros()
    quadros = quadros or []
    categorias, _ = api.get_categorias()
    categorias = categorias or []
    etiquetas, _ = api.get_etiquetas()
    etiquetas = etiquetas or []

    if not quadros:
        show_snackbar(page, "Cadastre um quadro primeiro para adicionar atividades.", is_error=True)
        return

    # Campos do formulário
    txt_titulo = ft.TextField(label="Título da Atividade *", autofocus=True)
    txt_descricao = ft.TextField(label="Descrição / Detalhes", multiline=True, min_lines=2, max_lines=4)
    txt_vencimento = ft.TextField(
        label="Data de Vencimento (AAAA-MM-DD)",
        value=preselected_date or date.today().strftime("%Y-%m-%d"),
        hint_text="Ex: 2026-11-20"
    )
    txt_observacoes = ft.TextField(label="Observações Adicionais", multiline=True, min_lines=1, max_lines=2)

    dd_prioridade = ft.Dropdown(
        label="Prioridade *",
        options=[
            ft.dropdown.Option("Baixa"),
            ft.dropdown.Option("Média"),
            ft.dropdown.Option("Alta"),
            ft.dropdown.Option("Urgente"),
        ],
        value="Média",
    )

    cat_options = [ft.dropdown.Option("0", "Sem Categoria")] + [
        ft.dropdown.Option(str(c["id"]), c["nome"]) for c in categorias
    ]
    dd_categoria = ft.Dropdown(label="Categoria", options=cat_options, value="0")

    # Dropdowns interdependentes: Quadro e Lista
    dd_quadro = ft.Dropdown(
        label="Quadro de Destino *",
        options=[ft.dropdown.Option(str(q["id"]), q["nome"]) for q in quadros],
        value=str(preselected_board_id) if preselected_board_id else str(quadros[0]["id"])
    )

    dd_lista = ft.Dropdown(label="Coluna / Lista de Destino *")

    def carregar_listas_do_quadro(qid):
        listas, _ = api.get_listas(quadro_id=int(qid))
        listas = listas or []
        dd_lista.options = [ft.dropdown.Option(str(l["id"]), l["nome"]) for l in listas]
        if listas:
            if preselected_list_id and any(str(l["id"]) == str(preselected_list_id) for l in listas):
                dd_lista.value = str(preselected_list_id)
            else:
                dd_lista.value = str(listas[0]["id"])
        else:
            dd_lista.value = None
        dd_lista.update()

    def on_quadro_change(e):
        if dd_quadro.value:
            carregar_listas_do_quadro(dd_quadro.value)

    dd_quadro.on_change = on_quadro_change

    # Etiquetas selecionáveis por checkboxes
    etiqueta_checkboxes = {}
    etiq_controls = []
    for et in etiquetas:
        cb = ft.Checkbox(label=et["nome"], value=False)
        etiqueta_checkboxes[et["id"]] = cb
        etiq_controls.append(cb)

    # Submeter
    def on_salvar(e):
        if not txt_titulo.value or not txt_titulo.value.strip():
            show_snackbar(page, "O título da atividade é obrigatório.", is_error=True)
            return
        if not dd_lista.value:
            show_snackbar(page, "Selecione uma lista de destino.", is_error=True)
            return

        cat_id = int(dd_categoria.value) if dd_categoria.value and dd_categoria.value != "0" else None
        selected_etiquetas = [eid for eid, cb in etiqueta_checkboxes.items() if cb.value]

        payload = {
            "titulo": txt_titulo.value.strip(),
            "descricao": txt_descricao.value.strip() if txt_descricao.value else None,
            "status": "A fazer",
            "prioridade": dd_prioridade.value or "Média",
            "data_vencimento": txt_vencimento.value.strip() if txt_vencimento.value else None,
            "observacoes": txt_observacoes.value.strip() if txt_observacoes.value else None,
            "lista_id": int(dd_lista.value),
            "categoria_id": cat_id,
            "etiqueta_ids": selected_etiquetas
        }

        res, err = api.create_atividade(payload)
        if err:
            show_snackbar(page, f"Erro ao criar atividade: {err}", is_error=True)
            return

        page.pop_dialog()
        show_snackbar(page, f"Atividade '{payload['titulo']}' criada com sucesso!")
        if on_success_callback:
            on_success_callback()

    # Montar diálogo
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.ADD_TASK_ROUNDED, color=COLOR_PRIMARY),
            ft.Text("Cadastrar Nova Atividade", weight=ft.FontWeight.BOLD, size=16),
        ], spacing=10),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    txt_titulo,
                    ft.Row([dd_quadro, dd_lista], spacing=12),
                    ft.Row([dd_prioridade, dd_categoria], spacing=12),
                    txt_vencimento,
                    txt_descricao,
                    txt_observacoes,
                    ft.Text("Etiquetas / Tags:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY),
                    ft.Row(controls=etiq_controls, wrap=True, spacing=8),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            ),
            width=520,
            height=460,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton(
                "Salvar Atividade",
                bgcolor=COLOR_PRIMARY,
                color=ft.Colors.WHITE,
                on_click=on_salvar
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(dlg)
    carregar_listas_do_quadro(dd_quadro.value)
    page.update()


def open_detalhes_atividade_modal(page: ft.Page, atividade_id: int, on_refresh_callback):
    """Abre modal interativo para visualizar, editar detalhes e gerenciar checklist da atividade."""
    atv, err = api.get_atividade(atividade_id)
    if err or not atv:
        show_snackbar(page, f"Erro ao carregar atividade: {err}", is_error=True)
        return

    txt_titulo = ft.TextField(label="Título", value=atv.get("titulo", ""))
    txt_descricao = ft.TextField(label="Descrição", value=atv.get("descricao") or "", multiline=True, min_lines=2, max_lines=4)
    txt_vencimento = ft.TextField(label="Data de Vencimento (AAAA-MM-DD)", value=atv.get("data_vencimento") or "")
    txt_observacoes = ft.TextField(label="Observações", value=atv.get("observacoes") or "", multiline=True, min_lines=1)

    dd_status = ft.Dropdown(
        label="Status",
        options=[
            ft.dropdown.Option("A fazer"),
            ft.dropdown.Option("Em andamento"),
            ft.dropdown.Option("Em revisão"),
            ft.dropdown.Option("Concluído"),
        ],
        value=atv.get("status", "A fazer")
    )

    dd_prioridade = ft.Dropdown(
        label="Prioridade",
        options=[
            ft.dropdown.Option("Baixa"),
            ft.dropdown.Option("Média"),
            ft.dropdown.Option("Alta"),
            ft.dropdown.Option("Urgente"),
        ],
        value=atv.get("prioridade", "Média")
    )

    # Checklist Interativo
    checklist_column = ft.Column(spacing=6)
    txt_novo_item = ft.TextField(hint_text="Nova subtarefa...", expand=True, dense=True)

    def recarregar_checklist():
        itens, _ = api.get_atividade(atividade_id)
        checklist_column.controls.clear()
        if itens and itens.get("checklists"):
            for item in itens["checklists"]:
                item_id = item["id"]
                cb = ft.Checkbox(
                    label=item["descricao"],
                    value=item["concluido"],
                )
                def on_toggle(e, iid=item_id, cb_ref=cb):
                    api.update_checklist_item(iid, {"concluido": cb_ref.value})
                    show_snackbar(page, "Checklist atualizado.")
                    recarregar_checklist()

                cb.on_change = on_toggle

                btn_del_item = ft.IconButton(
                    icon=ft.Icons.CLOSE_ROUNDED,
                    icon_size=16,
                    icon_color=COLOR_TEXT_SECONDARY,
                    tooltip="Excluir item",
                )
                def on_del_item(e, iid=item_id):
                    api.delete_checklist_item(iid)
                    recarregar_checklist()

                btn_del_item.on_click = on_del_item

                checklist_column.controls.append(
                    ft.Row([cb, ft.Container(expand=True), btn_del_item], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                )
        else:
            checklist_column.controls.append(
                ft.Text("Nenhuma subtarefa adicionada.", size=12, italic=True, color=COLOR_TEXT_SECONDARY)
            )
        checklist_column.update()

    def on_adicionar_item_checklist(e):
        if txt_novo_item.value and txt_novo_item.value.strip():
            api.add_checklist_item(atividade_id, {"descricao": txt_novo_item.value.strip(), "concluido": False})
            txt_novo_item.value = ""
            txt_novo_item.update()
            recarregar_checklist()

    # Ações principais
    def on_salvar_alteracoes(e):
        payload = {
            "titulo": txt_titulo.value.strip(),
            "descricao": txt_descricao.value.strip() if txt_descricao.value else None,
            "status": dd_status.value,
            "prioridade": dd_prioridade.value,
            "data_vencimento": txt_vencimento.value.strip() if txt_vencimento.value else None,
            "observacoes": txt_observacoes.value.strip() if txt_observacoes.value else None,
        }
        res, err = api.update_atividade(atividade_id, payload)
        if err:
            show_snackbar(page, f"Erro ao atualizar: {err}", is_error=True)
            return

        page.pop_dialog()
        show_snackbar(page, "Atividade atualizada com sucesso!")
        if on_refresh_callback:
            on_refresh_callback()

    def on_excluir_atividade(e):
        def confirmar_exclusao(ev):
            page.pop_dialog()  # Fecha confirmação
            api.delete_atividade(atividade_id)
            page.pop_dialog()  # Fecha detalhes
            show_snackbar(page, "Atividade removida.")
            if on_refresh_callback:
                on_refresh_callback()

        open_confirmacao_modal(
            page,
            f"Excluir atividade '{atv.get('titulo')}'?",
            "Esta ação não pode ser desfeita.",
            confirmar_exclusao
        )

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.TASK_ROUNDED, color=COLOR_PRIMARY),
            ft.Text(f"Detalhes da Atividade #{atividade_id}", weight=ft.FontWeight.BOLD, size=16),
            ft.Container(expand=True),
            ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=COLOR_DANGER, tooltip="Excluir Atividade", on_click=on_excluir_atividade)
        ]),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    txt_titulo,
                    ft.Row([dd_status, dd_prioridade], spacing=12),
                    txt_vencimento,
                    txt_descricao,
                    txt_observacoes,
                    ft.Divider(color=COLOR_BORDER),
                    ft.Text("Checklist de Subtarefas:", weight=ft.FontWeight.BOLD, size=13, color=COLOR_TEXT_PRIMARY),
                    checklist_column,
                    ft.Row([
                        txt_novo_item,
                        ft.IconButton(ft.Icons.ADD_CIRCLE_ROUNDED, icon_color=COLOR_PRIMARY, on_click=on_adicionar_item_checklist, tooltip="Adicionar subtarefa")
                    ]),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=12,
            ),
            width=520,
            height=480,
        ),
        actions=[
            ft.TextButton("Fechar", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton("Salvar Alterações", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=on_salvar_alteracoes),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.show_dialog(dlg)
    recarregar_checklist()
    page.update()


def open_novo_quadro_modal(page: ft.Page, on_success_callback):
    """Abre modal para criação de um novo quadro com cor personalizada."""
    txt_nome = ft.TextField(label="Nome do Quadro *", autofocus=True)
    txt_desc = ft.TextField(label="Descrição do Quadro", multiline=True, min_lines=2)
    selected_color = ft.Ref[str]()
    selected_color.current = PALETTE_PRESETS[0]

    color_chips = []
    for c in PALETTE_PRESETS:
        def on_color_click(e, color=c):
            selected_color.current = color
            show_snackbar(page, f"Cor {color} selecionada.")

        color_chips.append(
            ft.Container(
                width=28,
                height=28,
                border_radius=14,
                bgcolor=c,
                ink=True,
                on_click=on_color_click,
            )
        )

    def on_salvar(e):
        if not txt_nome.value or not txt_nome.value.strip():
            show_snackbar(page, "O nome do quadro é obrigatório.", is_error=True)
            return

        payload = {
            "nome": txt_nome.value.strip(),
            "descricao": txt_desc.value.strip() if txt_desc.value else None,
            "cor": selected_color.current or "#7C3AED"
        }
        res, err = api.create_quadro(payload)
        if err:
            show_snackbar(page, f"Erro: {err}", is_error=True)
            return

        page.pop_dialog()
        show_snackbar(page, f"Quadro '{payload['nome']}' criado com sucesso!")
        if on_success_callback:
            on_success_callback()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.DASHBOARD_CUSTOMIZE_ROUNDED, color=COLOR_PRIMARY),
            ft.Text("Novo Quadro Kanban", weight=ft.FontWeight.BOLD, size=16),
        ]),
        content=ft.Container(
            content=ft.Column(
                controls=[
                    txt_nome,
                    txt_desc,
                    ft.Text("Escolha a cor do quadro:", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT_SECONDARY),
                    ft.Row(controls=color_chips, wrap=True, spacing=8),
                ],
                spacing=14,
            ),
            width=420,
            height=260,
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton("Criar Quadro", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=on_salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)
    page.update()


def open_nova_lista_modal(page: ft.Page, quadro_id: int, on_success_callback):
    """Abre modal para adicionar nova coluna/lista ao quadro."""
    txt_nome = ft.TextField(label="Nome da Coluna / Lista *", autofocus=True)

    def on_salvar(e):
        if not txt_nome.value or not txt_nome.value.strip():
            show_snackbar(page, "O nome da lista é obrigatório.", is_error=True)
            return

        payload = {"nome": txt_nome.value.strip(), "quadro_id": quadro_id}
        res, err = api.create_lista(payload)
        if err:
            show_snackbar(page, f"Erro: {err}", is_error=True)
            return

        page.pop_dialog()
        show_snackbar(page, f"Coluna '{payload['nome']}' adicionada!")
        if on_success_callback:
            on_success_callback()

    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Nova Coluna no Quadro", weight=ft.FontWeight.BOLD, size=16),
        content=ft.Container(content=txt_nome, width=340, height=80),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton("Adicionar", bgcolor=COLOR_PRIMARY, color=ft.Colors.WHITE, on_click=on_salvar),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)
    page.update()


def open_confirmacao_modal(page: ft.Page, titulo: str, mensagem: str, on_confirm_callback):
    """Modal genérico de confirmação para ações destrutivas (excluir)."""
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Row([
            ft.Icon(ft.Icons.WARNING_ROUNDED, color=COLOR_DANGER),
            ft.Text(titulo, weight=ft.FontWeight.BOLD, size=16),
        ]),
        content=ft.Text(mensagem, size=13, color=COLOR_TEXT_SECONDARY),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: page.pop_dialog()),
            ft.ElevatedButton("Confirmar Exclusão", bgcolor=COLOR_DANGER, color=ft.Colors.WHITE, on_click=on_confirm_callback),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.show_dialog(dlg)
    page.update()
