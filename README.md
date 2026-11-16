# 🎓 StudyFlow — Sistema Inteligente de Gestão Acadêmica & Alta Performance

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Flask-3.0-black?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Gradio-Frontend%20SaaS-orange?style=for-the-badge&logo=gradio&logoColor=white" alt="Gradio" />
  <img src="https://img.shields.io/badge/SQLite-SQLAlchemy%20ORM-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/Swagger-OpenAPI%202.0-85EA2D?style=for-the-badge&logo=swagger&logoColor=black" alt="Swagger" />
  <img src="https://img.shields.io/badge/Status-100%25%20Funcional-success?style=for-the-badge" alt="Status" />
</p>

---

## 📌 1. Sobre o Projeto

O **StudyFlow** é um ecossistema completo de produtividade e gestão de estudos universitários projetado para centralizar disciplinas, entregas, cronogramas e sessões de foco em uma interface moderna, intuitiva e **100% responsiva** (adaptada para celulares, tablets, notebooks e desktops).

O sistema resolve os principais problemas enfrentados por estudantes no ensino superior:
- **Desorganização de prazos e acúmulo de entregas.**
- **Falta de clareza sobre quais tarefas são mais urgentes.**
- **Dificuldade de concentração e gerenciamento do tempo de estudo.**
- **Ausência de métricas visuais sobre o próprio desempenho acadêmico.**

### 🏛️ Arquitetura Desacoplada (Backend + Frontend)
O projeto segue as melhores práticas de engenharia de software com separação completa de responsabilidades:
1. **Backend RESTful (Flask 3 + SQLAlchemy ORM):**
   - API modular organizada em rotas (`/api/auth`, `/api/disciplinas`, `/api/atividades`, `/api/dashboard`).
   - Persistência relacional em banco de dados SQLite (`database/studyflow.db`).
   - Criptografia de senhas com algoritmo de hash seguro (`werkzeug.security`).
   - Documentação interativa **OpenAPI 2.0 / Swagger UI** disponível em `/apidocs/`.
2. **Frontend Visual Interativo (Gradio + HTML5/CSS3):**
   - Consome a API REST via requisições HTTP (`requests`).
   - Design moderno no padrão SaaS (Software as a Service) com tema claro, tipografia *Plus Jakarta Sans*, microinterações e sombras suaves.
   - Navegação mobile completa com **menu off-canvas (drawer lateral retrátil)** e botão hambúrguer.

---

## 🚀 2. Funcionalidades Principais

### 🏠 Landing Page SaaS
- **Apresentação Institucional:** Hero section moderna com proposta de valor, badges informativos e prévia da interface.
- **Seção de Recursos:** Cards explicativos dos módulos da plataforma.
- **Metodologia em 4 Etapas:** Passo a passo visual de planejamento semestral.
- **FAQ Interativo:** Perguntas frequentes com acordeões retráteis.
- **Rodapé Moderno:** Identidade oficial StudyFlow com atalhos vetoriais diretos para as principais seções da plataforma.

### 🔐 Autenticação & Isolamento de Dados
- **Cadastro de Estudantes:** Registro com validação de campos obrigatórios e hash criptográfico de senha.
- **Login Seguro:** Validação de credenciais e sessão individual por usuário.
- **Acesso Demo em 1 Clique:** Botão de login rápido com credenciais pré-configuradas para demonstração imediata (`aluno@studyflow.edu` / `123456`).

### ⏱️ Pomodoro Focus Hub
- **Temporizador Interativo:** Ciclos clássicos de 25 minutos de foco, 5 minutos de pausa curta e 15 minutos de pausa longa.
- **Ajustes de Tempo em Tempo Real:** Botões de incremento rápido (+1m / -1m).
- **Sons Ambientes Integrados (Web Audio API):** Áudio sintetizado diretamente no navegador sem dependências externas (Silêncio, Chuva relaxante e Ruído Marrom para foco profundo).
- **Contador de Ciclos Diários:** Monitoramento visual da quantidade de sessões de estudo concluídas no dia.

### 📝 Gestão de Atividades Acadêmicas (CRUD Completo)
- **Cadastro Rápido:** Título da atividade, disciplina vinculada, data de entrega (com validação de formato), nível de prioridade (Baixa, Média, Alta) e detalhes/orientações.
- **Tabela Interativa:** Seleção de registros com 1 clique para ações imediatas.
- **Filtros Dinâmicos em Tempo Real:** Filtragem simultânea por status (Pendente / Em Andamento / Concluída), nível de prioridade e busca textual.
- **Alternância de Conclusão Instantânea:** Marque como concluída ou reabra pendências com um clique.
- **Exclusão Segura:** Remoção de atividades com confirmação visual.

### ⚡ Algoritmo de Prioridade Preditiva
- O sistema calcula automaticamente o **índice de urgência** de cada tarefa combinando a proximidade da data de entrega com o peso da prioridade:
  - 🚨 **Atrasadas:** Alerta crítico no topo da lista.
  - ⚠️ **Vence Hoje:** Destaque visual prioritário.
  - ⏳ **Próximos 3 Dias:** Aviso preventivo.
  - 📅 **Planejadas:** Organizadas por ordem cronológica.

### 📅 Agenda & Calendário Mensal
- **Grade Mensal Colorida:** Visualização em calendário com badges coloridos por atividade conforme a matéria e status.
- **Cadastro Ágil via Calendário:** Formulário expansível para inserção direta de provas e trabalhos na grade do mês.
- **Toolbar com Controles:** Botão para alternar exibição do formulário e atualizar cronograma instantaneamente.

### 📊 Dashboard & Métricas de Produtividade
- **Cards Analíticos:** Total de atividades, tarefas concluídas, pendências ativas, trabalhos atrasados e entregas urgentes.
- **Barra de Produtividade:** Cálculo percentual da taxa de conclusão do semestre com gradiente visual dinâmico.
- **Progresso por Disciplina:** Métricas segmentadas por matéria para identificar onde é necessário reforçar os estudos.

### 📚 Categorias & Disciplinas (CRUD)
- **Cadastro de Matérias:** Nome da disciplina, professor responsável, cor de identificação e descrição da ementa.
- **Gestão Integrada:** Visualização de quantas tarefas estão vinculadas a cada disciplina cadastrada.
- **Exclusão Segura:** Prevenção de inconsistências no banco de dados.

### 📱 Responsividade Total (Mobile, Tablet & Desktop)
- **Smartphones (320px a 430px):** Menu hambúrguer funcional, drawer retrátil com backdrop blur, navbar em linha compacta, botões no formato pill autoajustáveis e formulários fluidos em coluna única.
- **Tablets (600px a 1024px):** Grid responsivo para cards, gráficos e tabelas adaptativas com rolagem horizontal controlada.
- **Notebooks & Desktops (1280px a 1920px+):** Layout completo em split-view com sidebar fixa e máxima ergonomia visual.

---

## 🛠️ 3. Tecnologias Utilizadas

| Camada | Tecnologia | Função no Ecossistema |
| :--- | :--- | :--- |
| **Linguagem** | Python 3.11 / 3.12 | Linguagem principal do backend e frontend |
| **Backend API** | Flask 3.0+ | Servidor HTTP RESTful e gerenciamento de rotas |
| **ORM / Banco** | SQLAlchemy + SQLite | Mapeamento objeto-relacional e persistência local |
| **Segurança** | Werkzeug Security | Hash criptográfico de senhas (PBKDF2-SHA256) |
| **Documentação** | Flasgger (OpenAPI 2.0) | Interface interativa Swagger UI em `/apidocs/` |
| **Frontend** | Gradio 6.x | Renderização reativa de componentes e blocos |
| **Comunicação** | Requests | Cliente HTTP para consumo desacoplado da API |
| **Manipulação** | Pandas | Estruturação e ordenação tabular de dados |
| **Testes** | Pytest 8.x / 9.x | Bateria de testes unitários automatizados |

---

## 📂 4. Estrutura do Repositório

```text
StudyFlow/
│
├── app.py                  # Fábrica da aplicação Flask, blueprints, Swagger e seed de dados
├── config.py               # Configurações do SQLAlchemy, banco SQLite e documentação
├── requirements.txt        # Lista de dependências Python
├── run.py                  # Script inicializador unificado (Backend + Frontend com 1 comando)
├── README.md               # Documentação técnica completa do projeto
├── .gitignore              # Arquivos e diretórios ignorados no controle de versão
│
├── database/
│   ├── database.py         # Instância do SQLAlchemy e rotina de criação das tabelas
│   └── studyflow.db        # Banco de dados relacional SQLite populado automaticamente
│
├── models/
│   ├── __init__.py
│   ├── usuario.py          # Modelo de dados da tabela 'usuarios' com hash de senha
│   ├── disciplina.py       # Modelo da tabela 'disciplinas' e relacionamento com atividades
│   └── atividade.py        # Modelo da tabela 'atividades' com algoritmo de urgência
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Endpoints /api/auth (cadastro e login com JWT/hash)
│   ├── disciplinas.py      # Endpoints RESTful /api/disciplinas (CRUD completo + Swagger)
│   ├── atividades.py       # Endpoints RESTful /api/atividades (CRUD + filtros + Swagger)
│   └── dashboard.py        # Endpoints /api/dashboard (métricas consolidadas e produtividade)
│
├── frontend/
│   ├── __init__.py
│   └── interface.py        # Interface visual Gradio SaaS, CSS responsivo e componentes
│
└── tests/
    ├── __init__.py
    └── test_api.py         # 12 testes unitários automatizados com pytest (CRUD, Auth e Swagger)
```

---

## 🔌 5. Endpoints da API REST & Documentação Swagger

A documentação interativa completa (onde é possível testar cada requisição diretamente pelo navegador) fica disponível em:
👉 **`http://127.0.0.1:5000/apidocs/`**

### Principais Rotas da API:

| Método | Endpoint | Descrição |
| :---: | :--- | :--- |
| `POST` | `/api/auth/cadastro` | Registra novo estudante com senha protegida |
| `POST` | `/api/auth/login` | Autentica estudante e inicia sessão |
| `GET` | `/api/dashboard` | Retorna métricas consolidadas, produtividade e alertas |
| `GET` | `/api/disciplinas` | Lista disciplinas cadastradas (filtro por estudante) |
| `POST` | `/api/disciplinas` | Cria nova matéria curricular |
| `GET` | `/api/disciplinas/<id>` | Retorna dados da matéria e suas atividades vinculadas |
| `PUT` | `/api/disciplinas/<id>` | Atualiza informações de uma matéria |
| `DELETE`| `/api/disciplinas/<id>` | Remove uma matéria com integridade referencial |
| `GET` | `/api/atividades` | Lista atividades (com filtros por status, prioridade e busca) |
| `POST` | `/api/atividades` | Cadastra nova atividade com data e prioridade |
| `GET` | `/api/atividades/<id>` | Retorna detalhes de uma atividade específica |
| `PUT` | `/api/atividades/<id>` | Atualiza dados de uma atividade |
| `PATCH`| `/api/atividades/<id>/status` | Alterna status (Pendente / Em Andamento / Concluída) |
| `DELETE`| `/api/atividades/<id>` | Exclui uma atividade acadêmica |

---

## ⚙️ 6. Como Executar o Projeto

### Pré-requisitos
- **Python 3.10, 3.11 ou 3.12** instalado no sistema.
- Gerenciador de pacotes **pip** atualizado.
- Git instalado (para clonar o repositório).

---

### Passo 1: Clonar o Repositório
Abra o terminal (Prompt de Comando, PowerShell ou Terminal do Linux/macOS) e clone o repositório oficial:
```bash
git clone https://github.com/marjorietalberg/StudyFlow.git
```

Acesse a pasta do projeto:
```bash
cd StudyFlow
```

---

### Passo 2: Criar e Ativar um Ambiente Virtual (Recomendado)

- **No Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

- **No Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### Passo 3: Instalar as Dependências
Com o ambiente ativado, instale todos os pacotes necessários com um único comando:
```bash
pip install -r requirements.txt
```

---

### Passo 4: Iniciar o Sistema Completo (Comando Único)
O StudyFlow conta com um orquestrador unificado (`run.py`) que sobe automaticamente o Backend Flask e o Frontend Gradio em paralelo:
```bash
python run.py
```

Assim que os servidores iniciarem, você verá a confirmação no terminal:
```text
=================================================================
🎓 StudyFlow - Sistema de Gestão Acadêmica & Produtividade
=================================================================
1️⃣ Iniciando Servidor Backend (Flask + Swagger) na porta 5000...
   ✅ Backend Flask operacional!

2️⃣ Links de Acesso:
   🌐 Frontend Gradio:       http://127.0.0.1:7860
   📚 Swagger Documentation:  http://127.0.0.1:5000/apidocs/
   ⚙️ API REST Root:         http://127.0.0.1:5000/
=================================================================
```

---

### Passo 5: Acessar no Navegador
- **Interface Completa do Aluno (Gradio):** [http://127.0.0.1:7860](http://127.0.0.1:7860)
- **Documentação Swagger UI da API:** [http://127.0.0.1:5000/apidocs/](http://127.0.0.1:5000/apidocs/)
- **Raiz da API REST (JSON):** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

> 💡 **Credenciais de Teste / Demonstração:**
> O banco de dados já é inicializado com dados realistas pré-populados. Para acessar instantaneamente:
> - Clique no botão **"Entrar"** na barra superior e utilize:
>   - **E-mail:** `aluno@studyflow.edu`
>   - **Senha:** `123456`
> - Ou clique no botão **"Preencher Demo"** para autenticação automática em 1 clique.

---

### Executando em Terminais Separados (Opcional)

Se preferir rodar cada serviço individualmente em janelas de terminal distintas:

**Terminal 1 — Backend Flask:**
```bash
python app.py
```

**Terminal 2 — Frontend Gradio:**
```bash
python frontend/interface.py
```

---

## 🧪 7. Executando os Testes Automatizados

O projeto inclui uma suíte completa de **12 testes unitários e de integração** desenvolvidos com `pytest`, validando os fluxos essenciais de negócio:
- Criação e validação de disciplinas e regras de integridade.
- Criação, atualização e alternância de status de atividades.
- Relacionamentos e cascata de exclusão.
- Retorno consistente do endpoint analítico de dashboard.
- Acessibilidade e resposta da documentação Swagger OpenAPI.

Para executar todos os testes automatizados:
```bash
python -m pytest tests/test_api.py -v
```

Resultado esperado:
```text
tests/test_api.py::test_criar_disciplina PASSED                          [  8%]
tests/test_api.py::test_criar_disciplina_invalida PASSED                 [ 16%]
tests/test_api.py::test_listar_disciplinas PASSED                        [ 25%]
tests/test_api.py::test_obter_disciplina_por_id PASSED                   [ 33%]
tests/test_api.py::test_atualizar_disciplina PASSED                      [ 41%]
tests/test_api.py::test_excluir_disciplina PASSED                        [ 50%]
tests/test_api.py::test_criar_atividade PASSED                           [ 58%]
tests/test_api.py::test_criar_atividade_sem_disciplina PASSED            [ 66%]
tests/test_api.py::test_alternar_status_atividade PASSED                 [ 75%]
tests/test_api.py::test_excluir_atividade PASSED                         [ 83%]
tests/test_api.py::test_obter_dashboard PASSED                           [ 91%]
tests/test_api.py::test_swagger_documentacao PASSED                      [100%]

============================= 12 passed in 14.80s =============================
```

---

## 🤖 8. Declaração Obrigatória de Uso de Inteligência Artificial

> *Conforme os critérios de avaliação acadêmica estipulados para a nota formativa N4, segue a discriminação transparente da utilização de ferramentas de Inteligência Artificial durante o desenvolvimento do projeto:*

### Percentual Efetivo de Uso de IA: **35%**

### Discriminação das Atividades:
- **Autoria do Estudante (65%):**
  - Definição da regra de negócio acadêmica e modelagem do banco de dados relacional (Usuários, Disciplinas e Atividades).
  - Arquitetura da aplicação em camadas desacopladas (`models/`, `routes/`, `database/`, `frontend/`, `tests/`).
  - Lógica de integração e consumo da API REST via biblioteca `requests` no frontend Gradio.
  - Testes manuais na interface, validação dos fluxos responsivos e parametrização dos cenários de teste automatizados.
  - Implementação do algoritmo ponderado de prioridade e lógica do cronograma mensal.
- **Apoio de Inteligência Artificial (35%):**
  - Geração das anotações OpenAPI/Swagger docstrings nos endpoints Flask.
  - Otimização do CSS responsivo para media queries e animações de transição suave.
  - Apoio no boilerplate dos fixtures de teste automatizado com SQLite in-memory.

---

## 📄 9. Licença & Créditos

Projeto desenvolvido para fins acadêmicos e educacionais como parte da avaliação de alto rendimento no semestre letivo.

- **Desenvolvido por:** Marjorie Talberg
- **Repositório Oficial:** [https://github.com/marjorietalberg/StudyFlow](https://github.com/marjorietalberg/StudyFlow)
- **Licença:** MIT License (Código aberto e livre para estudos acadêmicos).
