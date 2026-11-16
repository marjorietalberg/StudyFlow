# 💜 DayFlow — Gerenciador Inteligente de Atividades

> Plataforma completa de produtividade e gestão visual inspirada na experiência Kanban do **Trello** e em dashboards modernos de SaaS (Optima, Linear).

---

## 🌟 1. Visão Geral

O **DayFlow** foi desenvolvido para centralizar a organização de atividades pessoais, acadêmicas e profissionais em um ambiente visual moderno, intuitivo e responsivo.

- **Conceito Kanban Real**: Quadros, colunas/listas horizontais e cartões de tarefas.
- **Movimentação Ágil**: Botões de navegação rápida entre colunas que sincronizam instantaneamente o status da atividade no banco de dados.
- **Detecção Inteligente de Prazos**: Alertas visuais automáticos para tarefas atrasadas, tarefas que vencem hoje e próximas entregas.
- **Subtarefas (Checklist)**: Itens interativos com progresso dinâmico (ex: `2/3 concluídas`).
- **Arquitetura 100% Python**: Back-end robusto em **FastAPI** + Front-end reativo e elegante em **Flet**.
- **Persistência Total**: Banco de dados relacional **SQLite** com ORM **SQLAlchemy**.
- **Documentação Interativa**: Swagger UI automático em `/docs`.

---

## 🎨 2. Identidade Visual e Paleta

A estética do DayFlow segue os padrões de plataformas SaaS de alto padrão:

| Elemento | Cor Hex | Utilização |
|---|---|---|
| **Roxo Principal** | `#7C3AED` | Identidade visual, botões primários e destaque |
| **Roxo Secundário** | `#6D28D9` | Efeitos de hover e cabeçalhos |
| **Lavanda Suave** | `#EDE9FE` | Pílulas de seleção ativa e badges suaves |
| **Fundo Principal** | `#F8FAFC` | Fundo claro e limpo |
| **Superfície dos Cartões** | `#FFFFFF` | Cartões brancos com sombras suaves |
| **Texto Principal** | `#172033` | Títulos e textos de alta legibilidade |
| **Texto Secundário** | `#64748B` | Subtítulos, prazos e metadados |
| **Verde Sucesso** | `#10B981` | Tarefas e itens de checklist concluídos |
| **Laranja Atenção** | `#F59E0B` | Prioridade média e tarefas que vencem hoje |
| **Vermelho Alerta** | `#EF4444` | Tarefas atrasadas e prioridade urgente |

---

## 🏛️ 3. Estrutura do Projeto

```
dayflow/
│
├── backend/
│   ├── database.py             # Configuração da engine SQLite e SessionLocal
│   ├── models.py               # Modelos relacionais SQLAlchemy (Quadro, Lista, Atividade, Categoria, Etiqueta, Checklist)
│   ├── schemas.py              # Esquemas de validação de dados Pydantic
│   ├── seed_data.py            # Semeadura automática de dados realistas no primeiro uso
│   ├── main.py                 # Ponto de entrada FastAPI com CORS e Swagger
│   ├── routers/
│   │   ├── dashboard.py        # Métricas globais, percentuais de progresso e prazos
│   │   ├── quadros.py          # CRUD de quadros (cria 4 colunas padrão automaticamente)
│   │   ├── listas.py           # CRUD de colunas/listas dentro dos quadros
│   │   ├── atividades.py       # CRUD e movimentação PATCH de cartões
│   │   ├── categorias.py       # CRUD de categorias com cores personalizadas
│   │   ├── etiquetas.py        # CRUD de etiquetas (tags) com cores
│   │   └── checklist.py        # CRUD de subtarefas interativas
│   └── tests/
│       ├── test_dayflow_api.py # Testes de validação da API
│       └── run_tests.py        # Executor de testes automatizados
│
├── frontend/
│   ├── theme.py                # Definições de cores, presets e estilos visuais
│   ├── api_client.py           # Cliente HTTPx com timeout e tratamento de erros
│   ├── components/
│   │   ├── sidebar.py          # Menu lateral fixo com logo e navegação por pílulas
│   │   ├── header.py           # Barra superior com título, refresh e "+ Nova Atividade"
│   │   └── modals.py           # Modais de cadastro, checklist, edição e confirmação
│   ├── pages/
│   │   ├── dashboard.py        # Painel de métricas executivas, progresso e próximas entregas
│   │   ├── quadros.py          # Grade de quadros com percentual de conclusão
│   │   ├── kanban.py           # Quadro Kanban visual estilo Trello
│   │   ├── atividades.py       # Consulta tabular com busca global e filtros combinados
│   │   ├── calendario.py       # Grade mensal interativa com tarefas por data
│   │   ├── categorias.py       # Gestão completa de categorias e etiquetas (tags)
│   │   └── concluidas.py       # Histórico de atividades finalizadas e botão de reabertura
│   └── main.py                 # Interface Flet em modo Web Browser
│
├── run.py                      # Launcher simultâneo (Backend + Frontend)
├── requirements.txt            # Dependências oficiais
└── README.md                   # Documentação do sistema
```

---

## 🚀 4. Como Executar

### 1. Instalação das dependências
```bash
pip install -r dayflow/requirements.txt
```

### 2. Inicialização completa em um único comando
```bash
python dayflow/run.py
```

### Ou inicialização individual:
- **Backend FastAPI**:
  ```bash
  python dayflow/backend/main.py
  ```
  *Acesso API & Swagger:* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

- **Frontend Flet Web**:
  ```bash
  python dayflow/frontend/main.py
  ```
  *Acesso Interface Web:* [http://127.0.0.1:8550](http://127.0.0.1:8550)

---

## 📋 5. Telas e Funcionalidades

### 5.1 Dashboard Executivo
- Saudação com data em tempo real.
- **KPIs em Destaque**: Total de Atividades, A Fazer, Em Andamento, Em Revisão e Concluídas.
- **Barra de Progresso Geral**: Cálculo automático do percentual de tarefas finalizadas.
- **Card de Alerta**: Destaque para tarefas atrasadas e compromissos que vencem hoje.
- **Divisão Central**: Cartões com as próximas entregas e atividades criadas recentemente.

### 5.2 Meus Quadros
- Cartões com faixas coloridas personalizadas por quadro.
- Métricas específicas de cada quadro (total de listas, atividades e barra de progresso individual).
- Modal para criação de novos quadros com seletor de paleta de cores.
- Botão "Abrir Quadro Kanban" para navegação instantânea.

### 5.3 Quadro Kanban Visual (Trello-inspired)
- Colunas horizontais: **A fazer**, **Em andamento**, **Em revisão** e **Concluído** (com suporte a colunas customizadas).
- Seletor suspenso no topo para alternar entre os quadros.
- Cartões com identificador de prioridade (*Baixa*, *Média*, *Alta*, *Urgente*), etiquetas coloridas, contador de subtarefas (`1/3`) e badge de prazo.
- **Botões de Movimentação**: `◀` e `▶` em cada cartão que movem a tarefa entre colunas e atualizam automaticamente o status no banco de dados via API.
- Clique no cartão abre a janela com checklist interativo, observações e opções de edição.

### 5.4 Minhas Atividades (Lista Unificada)
- Busca em tempo real por título e descrição.
- Filtro por Status (*Todos*, *A fazer*, *Em andamento*, *Em revisão*, *Concluído*).
- Filtro por Prioridade (*Todas*, *Baixa*, *Média*, *Alta*, *Urgente*).
- Filtro por Prazo (*Todos*, *Atrasadas*, *Vencem Hoje*, *Próxima Semana*).

### 5.5 Agenda e Calendário
- Matriz mensal completa com navegação por meses (*Anterior*, *Hoje*, *Próximo*).
- Destaque visual para o dia atual e indicador numérico de tarefas em cada dia do mês.
- Painel lateral que lista detalhadamente as atividades do dia selecionado.
- Botão para cadastrar uma nova atividade diretamente na data escolhida.

### 5.6 Categorias & Etiquetas (Tags)
- Painel duplo para criação e exclusão de categorias e etiquetas.
- Cores configuráveis para fácil identificação visual nos cartões.

### 5.7 Atividades Concluídas (Histórico)
- Registro completo de entregas concluídas com data de finalização.
- Botão **"Reabrir Atividade"**, que recoloca a tarefa de volta no fluxo Kanban (`Em andamento`).

---

## 🧪 6. Testes Automatizados

O sistema conta com suíte de testes de integração da API REST que valida todos os endpoints CRUD, criação de listas padrão e integridade do banco:
```bash
python dayflow/backend/tests/run_tests.py
```
Resultado: **100% dos testes aprovados com sucesso.**
