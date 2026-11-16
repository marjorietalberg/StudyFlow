from datetime import date, datetime
from database.database import db

class Atividade(db.Model):
    __tablename__ = 'atividades'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    disciplina_id = db.Column(db.Integer, db.ForeignKey('disciplinas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    data_entrega = db.Column(db.String(10), nullable=False)  # Formato YYYY-MM-DD
    prioridade = db.Column(db.String(20), nullable=False, default='Média')  # Baixa, Média, Alta
    status = db.Column(db.String(20), nullable=False, default='Pendente')  # Pendente, Em Andamento, Concluída

    @property
    def dias_restantes(self):
        """Calcula a quantidade de dias restantes até a data de entrega."""
        try:
            hoje = date.today()
            prazo = datetime.strptime(self.data_entrega, '%Y-%m-%d').date()
            return (prazo - hoje).days
        except Exception:
            return None

    @property
    def is_atrasada(self):
        """Retorna True se a atividade estiver fora do prazo e não concluída."""
        if self.status == 'Concluída':
            return False
        dias = self.dias_restantes
        return dias is not None and dias < 0

    @property
    def alerta_prazo(self):
        """Gera um status textual inteligente sobre o prazo da atividade."""
        if self.status == 'Concluída':
            return 'Concluída'
        dias = self.dias_restantes
        if dias is None:
            return 'Sem data'
        if dias < 0:
            return f'Atrasada ({abs(dias)}d)'
        elif dias == 0:
            return 'Vence Hoje!'
        elif dias == 1:
            return 'Vence Amanhã'
        elif dias <= 3:
            return f'Vence em {dias} dias'
        else:
            return f'Em {dias} dias'

    @property
    def score_urgencia(self):
        """Calcula prioridade inteligente: quanto maior, mais urgente."""
        if self.status == 'Concluída':
            return 0
        dias = self.dias_restantes
        peso_prioridade = {'Urgente': 50, 'Alta': 30, 'Média': 20, 'Baixa': 10}.get(self.prioridade, 20)
        if dias is None:
            return peso_prioridade
        if dias < 0:
            return 1000 + abs(dias) * 10 + peso_prioridade  # Atrasadas têm máxima prioridade
        elif dias == 0:
            return 500 + peso_prioridade
        elif dias <= 3:
            return 200 + (3 - dias) * 20 + peso_prioridade
        else:
            return max(1, 100 - dias) + peso_prioridade

    def to_dict(self):
        disc_cor = '#7c3aed'
        if self.disciplina and hasattr(self.disciplina, 'cor') and self.disciplina.cor:
            disc_cor = self.disciplina.cor
        return {
            'id': self.id,
            'titulo': self.titulo,
            'descricao': self.descricao or '',
            'disciplina_id': self.disciplina_id,
            'disciplina_nome': self.disciplina.nome if self.disciplina else 'Geral',
            'disciplina_cor': disc_cor,
            'usuario_id': self.usuario_id,
            'data_entrega': self.data_entrega,
            'prioridade': self.prioridade,
            'status': self.status,
            'dias_restantes': self.dias_restantes,
            'is_atrasada': self.is_atrasada,
            'alerta_prazo': self.alerta_prazo,
            'score_urgencia': self.score_urgencia
        }

    def __repr__(self):
        return f'<Atividade {self.titulo} - {self.status}>'
