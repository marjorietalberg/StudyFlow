from datetime import datetime
from flask import Blueprint, request, jsonify
from database.database import db
from models.atividade import Atividade
from models.disciplina import Disciplina

atividades_bp = Blueprint('atividades', __name__, url_prefix='/api/atividades')

@atividades_bp.route('', methods=['GET'])
def listar_atividades():
    """
    Listar atividades com filtros opcionais
    ---
    tags:
      - Atividades
    parameters:
      - in: query
        name: status
        type: string
        description: Filtrar por status (Pendente, Em Andamento, Concluída)
      - in: query
        name: prioridade
        type: string
        description: Filtrar por prioridade (Baixa, Média, Alta)
      - in: query
        name: disciplina_id
        type: integer
        description: Filtrar por ID da disciplina
      - in: query
        name: inteligente
        type: boolean
        description: Se true, ordena por prioridade inteligente (urgência/atraso)
    responses:
      200:
        description: Lista de atividades
    """
    query = Atividade.query

    status_filter = request.args.get('status')
    prioridade_filter = request.args.get('prioridade')
    disciplina_id = request.args.get('disciplina_id')
    usuario_id = request.args.get('usuario_id')
    inteligente_param = request.args.get('inteligente') or request.args.get('ordenar_inteligente', 'false')
    inteligente = str(inteligente_param).lower() == 'true'

    if usuario_id:
        try:
            query = query.filter_by(usuario_id=int(usuario_id))
        except ValueError:
            pass
    if status_filter:
        query = query.filter_by(status=status_filter)
    if prioridade_filter:
        query = query.filter_by(prioridade=prioridade_filter)
    if disciplina_id:
        try:
            query = query.filter_by(disciplina_id=int(disciplina_id))
        except ValueError:
            pass

    atividades = query.all()

    if inteligente:
        # Ordena pelo score de urgência descrescente (atrasadas e prazos próximos no topo)
        atividades = sorted(atividades, key=lambda a: a.score_urgencia, reverse=True)
    else:
        # Ordenação padrão por data de entrega crescente e com desempate por urgência
        atividades = sorted(atividades, key=lambda a: (a.data_entrega, -a.score_urgencia))

    return jsonify([a.to_dict() for a in atividades]), 200


@atividades_bp.route('/<int:id>', methods=['GET'])
def obter_atividade(id):
    """
    Buscar detalhes de uma atividade pelo ID
    ---
    tags:
      - Atividades
    parameters:
      - in: path
        name: id
        required: true
        type: integer
    responses:
      200:
        description: Detalhes da atividade
      404:
        description: Atividade não encontrada
    """
    atividade = db.session.get(Atividade, id)
    if not atividade:
        return jsonify({'error': 'Atividade não encontrada'}), 404
    return jsonify(atividade.to_dict()), 200


@atividades_bp.route('', methods=['POST'])
def criar_atividade():
    """
    Cadastrar uma nova atividade acadêmica
    ---
    tags:
      - Atividades
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - titulo
            - disciplina_id
            - data_entrega
          properties:
            titulo:
              type: string
              example: Implementação da API REST
            descricao:
              type: string
              example: Desenvolver CRUD com SQLAlchemy e documentar via Swagger
            disciplina_id:
              type: integer
              example: 1
            data_entrega:
              type: string
              example: "2026-11-20"
            prioridade:
              type: string
              enum: [Baixa, Média, Alta]
              example: Alta
            status:
              type: string
              enum: [Pendente, Em Andamento, Concluída]
              example: Pendente
    responses:
      201:
        description: Atividade criada com sucesso
      400:
        description: Dados inválidos
      404:
        description: Disciplina informada não existe
    """
    dados = request.get_json(silent=True) or {}
    titulo = dados.get('titulo', '').strip()
    descricao = dados.get('descricao', '').strip()
    disciplina_id = dados.get('disciplina_id')
    usuario_id = dados.get('usuario_id')
    data_entrega = dados.get('data_entrega', '').strip()
    
    # Normalização robusta de prioridade (suporta acentuado, sem acento, caixa alta/baixa)
    prioridade_raw = str(dados.get('prioridade') or 'Média').strip().lower()
    if prioridade_raw in ['alta', 'alto', 'high']:
        prioridade = 'Alta'
    elif prioridade_raw in ['baixa', 'baixo', 'low']:
        prioridade = 'Baixa'
    else:
        prioridade = 'Média'

    status = dados.get('status', 'Pendente').strip()

    if not titulo:
        return jsonify({'error': 'O campo "titulo" é obrigatório.'}), 400
    if not disciplina_id:
        return jsonify({'error': 'O campo "disciplina_id" é obrigatório.'}), 400
    if not data_entrega:
        return jsonify({'error': 'O campo "data_entrega" é obrigatório (formato YYYY-MM-DD).'}), 400

    # Validar formato de data
    try:
        datetime.strptime(data_entrega, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Formato de "data_entrega" inválido. Utilize YYYY-MM-DD.'}), 400

    # Validar se disciplina existe
    disciplina = db.session.get(Disciplina, disciplina_id)
    if not disciplina:
        return jsonify({'error': f'Disciplina com ID {disciplina_id} não encontrada.'}), 404

    # Validar prioridade e status
    status_validos = ['Backlog', 'Pendente', 'A Fazer', 'Em Andamento', 'Em Validação', 'Em Revisão', 'Concluída']
    prioridades_validas = ['Baixa', 'Média', 'Alta', 'Urgente']

    if prioridade not in prioridades_validas:
        prioridade = 'Média'
    if status not in status_validos:
        status = 'Pendente'

    nova_atividade = Atividade(
        titulo=titulo,
        descricao=descricao,
        disciplina_id=disciplina_id,
        usuario_id=usuario_id,
        data_entrega=data_entrega,
        prioridade=prioridade,
        status=status
    )
    db.session.add(nova_atividade)
    db.session.commit()

    return jsonify(nova_atividade.to_dict()), 201


@atividades_bp.route('/<int:id>', methods=['PUT'])
def atualizar_atividade(id):
    """
    Atualizar dados de uma atividade
    ---
    tags:
      - Atividades
    parameters:
      - in: path
        name: id
        required: true
        type: integer
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            titulo:
              type: string
            descricao:
              type: string
            disciplina_id:
              type: integer
            data_entrega:
              type: string
            prioridade:
              type: string
            status:
              type: string
    responses:
      200:
        description: Atividade atualizada com sucesso
      404:
        description: Atividade não encontrada
    """
    atividade = db.session.get(Atividade, id)
    if not atividade:
        return jsonify({'error': 'Atividade não encontrada'}), 404

    dados = request.get_json(silent=True) or {}

    if 'titulo' in dados and dados['titulo'].strip():
        atividade.titulo = dados['titulo'].strip()
    if 'descricao' in dados:
        atividade.descricao = dados['descricao'].strip()
    if 'disciplina_id' in dados:
        disc = db.session.get(Disciplina, dados['disciplina_id'])
        if not disc:
            return jsonify({'error': 'Disciplina informada não existe.'}), 404
        atividade.disciplina_id = dados['disciplina_id']
    if 'data_entrega' in dados and dados['data_entrega'].strip():
        try:
            datetime.strptime(dados['data_entrega'].strip(), '%Y-%m-%d')
            atividade.data_entrega = dados['data_entrega'].strip()
        except ValueError:
            return jsonify({'error': 'Formato de "data_entrega" inválido. Utilize YYYY-MM-DD.'}), 400
    status_validos = ['Backlog', 'Pendente', 'A Fazer', 'Em Andamento', 'Em Validação', 'Em Revisão', 'Concluída']
    prioridades_validas = ['Baixa', 'Média', 'Alta', 'Urgente']

    if 'prioridade' in dados:
        p = dados['prioridade'].strip().capitalize()
        if p in prioridades_validas:
            atividade.prioridade = p
    if 'status' in dados:
        s = dados['status'].strip()
        if s in status_validos:
            atividade.status = s

    db.session.commit()
    return jsonify(atividade.to_dict()), 200


@atividades_bp.route('/<int:id>/status', methods=['PATCH'])
def atualizar_status(id):
    """
    Alternar ou atualizar status rapidamente de uma atividade
    ---
    tags:
      - Atividades
    parameters:
      - in: path
        name: id
        required: true
        type: integer
      - in: body
        name: body
        required: false
        schema:
          type: object
          properties:
            status:
              type: string
              example: Concluída
    responses:
      200:
        description: Status atualizado com sucesso
      404:
        description: Atividade não encontrada
    """
    atividade = db.session.get(Atividade, id)
    if not atividade:
        return jsonify({'error': 'Atividade não encontrada'}), 404

    dados = request.get_json(silent=True) or {}
    novo_status = dados.get('status', '').strip()

    if not novo_status:
        # Alterna entre Concluída e Pendente se nenhum status for fornecido
        novo_status = 'Pendente' if atividade.status == 'Concluída' else 'Concluída'

    status_validos = ['Backlog', 'Pendente', 'A Fazer', 'Em Andamento', 'Em Validação', 'Em Revisão', 'Concluída']
    if novo_status not in status_validos:
        return jsonify({'error': f'Status inválido. Escolha um dos seguintes: {", ".join(status_validos)}.'}), 400

    atividade.status = novo_status
    db.session.commit()
    return jsonify(atividade.to_dict()), 200


@atividades_bp.route('/<int:id>', methods=['DELETE'])
def excluir_atividade(id):
    """
    Excluir uma atividade acadêmica
    ---
    tags:
      - Atividades
    parameters:
      - in: path
        name: id
        required: true
        type: integer
    responses:
      200:
        description: Atividade removida com sucesso
      404:
        description: Atividade não encontrada
    """
    atividade = db.session.get(Atividade, id)
    if not atividade:
        return jsonify({'error': 'Atividade não encontrada'}), 404

    db.session.delete(atividade)
    db.session.commit()
    return jsonify({'message': f'Atividade "{atividade.titulo}" (ID {id}) removida com sucesso.'}), 200
