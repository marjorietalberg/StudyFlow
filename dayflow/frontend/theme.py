# Cores principais da identidade visual do DayFlow
COLOR_PRIMARY = "#7C3AED"       # Roxo principal
COLOR_PRIMARY_HOVER = "#6D28D9" # Roxo secundário
COLOR_PRIMARY_LIGHT = "#EDE9FE" # Lavanda suave
COLOR_BG = "#F8FAFC"            # Fundo principal claro
COLOR_SURFACE = "#FFFFFF"       # Superfície dos cartões
COLOR_SURFACE_ALT = "#F1F5F9"   # Cinza suave para colunas e cabeçalhos
COLOR_TEXT_PRIMARY = "#172033"  # Texto principal grafite escuro
COLOR_TEXT_SECONDARY = "#64748B"# Texto secundário
COLOR_BORDER = "#E2E8F0"        # Borda sutil
COLOR_BORDER_LIGHT = "#CBD5E1"  # Borda ativa

# Cores de status e prioridades
COLOR_SUCCESS = "#10B981"       # Verde para concluídas
COLOR_SUCCESS_BG = "#D1FAE5"    # Fundo verde suave
COLOR_WARNING = "#F59E0B"       # Laranja para atenção / média
COLOR_WARNING_BG = "#FEF3C7"    # Fundo amarelo suave
COLOR_DANGER = "#EF4444"        # Vermelho para atrasadas / urgente
COLOR_DANGER_BG = "#FEE2E2"     # Fundo vermelho suave
COLOR_INFO = "#3B82F6"          # Azul informativo
COLOR_INFO_BG = "#DBEAFE"       # Fundo azul suave

# Paleta para seleção de cores de Quadros e Categorias
PALETTE_PRESETS = [
    "#7C3AED",  # Roxo DayFlow
    "#4F46E5",  # Índigo
    "#2563EB",  # Azul Royal
    "#0284C7",  # Ciano Oceano
    "#0D9488",  # Verde Petróleo
    "#10B981",  # Esmeralda
    "#D97706",  # Âmbar Dourado
    "#EA580C",  # Laranja
    "#E11D48",  # Rosa Escarlate
    "#475569"   # Grafite Neutro
]

# Mapeamento de estilos por prioridade
PRIORITY_COLORS = {
    "Baixa": {"text": "#475569", "bg": "#F1F5F9", "border": "#CBD5E1"},
    "Média": {"text": "#D97706", "bg": "#FEF3C7", "border": "#FDE68A"},
    "Alta": {"text": "#7C3AED", "bg": "#EDE9FE", "border": "#DDD6FE"},
    "Urgente": {"text": "#DC2626", "bg": "#FEE2E2", "border": "#FECACA"},
}

# Mapeamento de status
STATUS_COLORS = {
    "A fazer": {"text": "#475569", "bg": "#F1F5F9"},
    "Em andamento": {"text": "#2563EB", "bg": "#DBEAFE"},
    "Em revisão": {"text": "#D97706", "bg": "#FEF3C7"},
    "Concluído": {"text": "#10B981", "bg": "#D1FAE5"},
}
