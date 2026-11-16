from database.database import db

class Disciplina(db.Model):
    __tablename__ = 'disciplinas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    professor = db.Column(db.String(100), nullable=True, default='Geral')
    descricao = db.Column(db.String(255), nullable=True)
    cor = db.Column(db.String(30), nullable=True, default='#7c3aed')
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    # Relacionamento 1:N com Atividade
    atividades = db.relationship('Atividade', backref='disciplina', lazy=True, cascade='all, delete-orphan')

    def to_dict(self, include_atividades=False):
        data = {
            'id': self.id,
            'nome': self.nome,
            'professor': self.professor or 'Geral',
            'descricao': self.descricao or '',
            'cor': self.cor or '#7c3aed',
            'usuario_id': self.usuario_id,
            'total_atividades': len(self.atividades)
        }
        if include_atividades:
            data['atividades'] = [a.to_dict() for a in self.atividades]
        return data

    def __repr__(self):
        return f'<Disciplina {self.nome}>'
