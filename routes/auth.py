from flask import Blueprint, request, jsonify
from database.database import db
from models.usuario import Usuario

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/cadastro', methods=['POST'])
def cadastrar_usuario():
    """
    Cadastrar um novo estudante no StudyFlow
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nome
            - email
            - senha
          properties:
            nome:
              type: string
              example: Marjorie Talberg
            email:
              type: string
              example: marjorie@universidade.edu.br
            senha:
              type: string
              example: 123456
            curso:
              type: string
              example: Engenharia de Software
    responses:
      201:
        description: Usuário cadastrado com sucesso
      400:
        description: E-mail já cadastrado ou campos obrigatórios ausentes
    """
    dados = request.get_json(silent=True) or {}
    nome = dados.get('nome', '').strip()
    email = dados.get('email', '').strip().lower()
    senha = dados.get('senha', '').strip()
    curso = dados.get('curso', 'Engenharia de Software').strip()

    if not nome or not email or not senha:
        return jsonify({'error': 'Nome, e-mail e senha são obrigatórios.'}), 400

    if '@' not in email or '.' not in email:
        return jsonify({'error': 'E-mail com formato inválido.'}), 400

    # Verifica se e-mail já existe
    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        return jsonify({'error': 'Este e-mail já está em uso por outro estudante.'}), 400

    novo_usuario = Usuario(
        nome=nome,
        email=email,
        curso=curso
    )
    novo_usuario.set_senha(senha)

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({
        'message': 'Conta criada com sucesso!',
        'usuario': novo_usuario.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Autenticar estudante com e-mail e senha
    ---
    tags:
      - Autenticação
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - senha
          properties:
            email:
              type: string
              example: marjorie@universidade.edu.br
            senha:
              type: string
              example: 123456
    responses:
      200:
        description: Login realizado com sucesso
      401:
        description: Credenciais inválidas
    """
    dados = request.get_json(silent=True) or {}
    email = dados.get('email', '').strip().lower()
    senha = dados.get('senha', '').strip()

    if not email or not senha:
        return jsonify({'error': 'Informe seu e-mail acadêmico e senha cadastrados para entrar.'}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({'error': 'Este e-mail não foi encontrado no sistema. Cadastre-se na aba "Criar Nova Conta" primeiro.'}), 401

    if not usuario.checar_senha(senha):
        return jsonify({'error': 'Senha incorreta para o e-mail acadêmico informado.'}), 401

    return jsonify({
        'message': f'Bem-vindo de volta, {usuario.nome}!',
        'usuario': usuario.to_dict()
    }), 200


@auth_bp.route('/usuario/<int:id>', methods=['GET'])
def obter_perfil(id):
    """
    Obter dados do perfil do estudante
    ---
    tags:
      - Autenticação
    parameters:
      - in: path
        name: id
        required: true
        type: integer
    responses:
      200:
        description: Dados do perfil
      404:
        description: Usuário não encontrado
    """
    usuario = db.session.get(Usuario, id)
    if not usuario:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify(usuario.to_dict()), 200
