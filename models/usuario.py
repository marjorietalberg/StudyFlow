from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from database.database import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    curso = db.Column(db.String(100), nullable=True, default='Ciência da Computação')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    disciplinas = db.relationship('Disciplina', backref='usuario', lazy=True, cascade='all, delete-orphan')
    atividades = db.relationship('Atividade', backref='usuario', lazy=True, cascade='all, delete-orphan')

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def checar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'curso': self.curso or 'Estudante',
            'criado_em': self.criado_em.strftime('%Y-%m-%d %H:%M:%S') if self.criado_em else ''
        }

    def __repr__(self):
        return f'<Usuario {self.nome} ({self.email})>'
