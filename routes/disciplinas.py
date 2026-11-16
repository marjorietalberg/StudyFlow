from flask import Blueprint, request, jsonify
from database.database import db
from models.disciplina import Disciplina

disciplinas_bp = Blueprint('disciplinas', __name__, url_prefix='/api/disciplinas')

@disciplinas_bp.route('', methods=['GET'])
def listar_disciplinas():
    """
    Listar todas as disciplinas cadastradas
    ---
    tags:
      - Disciplinas
    parameters:
      - in: query
        name: usuario_id
        type: integer
        description: Filtrar disciplinas do usuário logado
    responses:
      200:
        description: Lista de disciplinas cadastradas
    """
    query = Disciplina.query
    usuario_id = request.args.get('usuario_id')
    if usuario_id:
        try:
            query = query.filter_by(usuario_id=int(usuario_id))
        except ValueError:
            pass

    disciplinas = query.order_by(Disciplina.nome.asc()).all()
    return jsonify([d.to_dict() for d in disciplinas]), 200


@disciplinas_bp.route('/<int:id>', methods=['GET'])
def obter_disciplina(id):
    """
    Obter detalhes de uma disciplina pelo ID (inclui suas atividades)
    ---
    tags:
      - Disciplinas
    parameters:
      - in: path
        name: id
        required: true
        type: integer
        description: ID da disciplina
    responses:
      200:
        description: Dados da disciplina
      404:
        description: Disciplina não encontrada
    """
    disciplina = db.session.get(Disciplina, id)
    if not disciplina:
        return jsonify({'error': 'Disciplina não encontrada'}), 404
    return jsonify(disciplina.to_dict(include_atividades=True)), 200


@disciplinas_bp.route('', methods=['POST'])
def criar_disciplina():
    """
    Cadastrar uma nova disciplina
    ---
    tags:
      - Disciplinas
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - professor
          properties:
            nome:
              type: string
              example: Engenharia de Software
            professor:
              type: string
              example: Prof. Carlos Silva
            descricao:
              type: string
              example: Conceitos de desenvolvimento ágil e arquitetura de software
    responses:
      201:
        description: Disciplina criada com sucesso
      400:
        description: Dados inválidos ou campos obrigatórios ausentes
    """
    dados = request.get_json(silent=True) or {}
    nome = dados.get('nome', '').strip()
    professor = dados.get('professor', '').strip() or 'Geral'
    descricao = dados.get('descricao', '').strip()
    cor = dados.get('cor', '').strip() or '#7c3aed'
    usuario_id = dados.get('usuario_id')

    if not nome:
        return jsonify({'error': 'O campo "nome" é obrigatório.'}), 400

    nova_disciplina = Disciplina(
        nome=nome,
        professor=professor,
        descricao=descricao,
        cor=cor,
        usuario_id=usuario_id
    )
    db.session.add(nova_disciplina)
    db.session.commit()

    return jsonify(nova_disciplina.to_dict()), 201


@disciplinas_bp.route('/<int:id>', methods=['PUT'])
def atualizar_disciplina(id):
    """
    Atualizar os dados de uma disciplina existente
    ---
    tags:
      - Disciplinas
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
            nome:
              type: string
            professor:
              type: string
            descricao:
              type: string
    responses:
      200:
        description: Disciplina atualizada com sucesso
      404:
        description: Disciplina não encontrada
    """
    disciplina = db.session.get(Disciplina, id)
    if not disciplina:
        return jsonify({'error': 'Disciplina não encontrada'}), 404

    dados = request.get_json(silent=True) or {}
    if 'nome' in dados and dados['nome'].strip():
        disciplina.nome = dados['nome'].strip()
    if 'professor' in dados and dados['professor'].strip():
        disciplina.professor = dados['professor'].strip()
    if 'descricao' in dados:
        disciplina.descricao = dados['descricao'].strip()
    if 'cor' in dados and dados['cor'].strip():
        disciplina.cor = dados['cor'].strip()

    db.session.commit()
    return jsonify(disciplina.to_dict()), 200


@disciplinas_bp.route('/<int:id>', methods=['DELETE'])
def excluir_disciplina(id):
    """
    Excluir uma disciplina pelo ID
    ---
    tags:
      - Disciplinas
    parameters:
      - in: path
        name: id
        required: true
        type: integer
    responses:
      200:
        description: Disciplina removida com sucesso
      404:
        description: Disciplina não encontrada
    """
    disciplina = db.session.get(Disciplina, id)
    if not disciplina:
        return jsonify({'error': 'Disciplina não encontrada'}), 404

    db.session.delete(disciplina)
    db.session.commit()
    return jsonify({'message': f'Disciplina {disciplina.nome} (ID {id}) removida com sucesso.'}), 200
