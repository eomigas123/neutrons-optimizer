"""
Paleta de cores do tema Nêutrons.
"""

class NeutronColors:
    """Cores do tema Nêutrons Optimizer."""
    
    # Cores base
    BACKGROUND = "#0e1220"
    SURFACE = "#1a2332"
    SURFACE_VARIANT = "#242f42"
    
    # Cores de acento
    PRIMARY = "#22d3ee"          # Cyan brilhante
    SECONDARY = "#60a5fa"        # Azul médio
    ACCENT = "#8b5cf6"           # Roxo discreto
    
    # Estados
    SUCCESS = "#10b981"          # Verde
    WARNING = "#f59e0b"          # Amarelo
    ERROR = "#ef4444"            # Vermelho
    INFO = "#3b82f6"             # Azul
    
    # Textos
    TEXT_PRIMARY = "#f8fafc"     # Branco quase puro
    TEXT_SECONDARY = "#cbd5e1"   # Cinza claro
    TEXT_MUTED = "#64748b"       # Cinza médio
    TEXT_DISABLED = "#475569"    # Cinza escuro
    
    # Bordas e divisores
    BORDER = "#334155"
    BORDER_LIGHT = "#475569"
    DIVIDER = "#1e293b"
    
    # Hover e focus
    HOVER = "#2d3748"
    FOCUS = "#4a5568"
    SELECTED = "#2563eb"
    
    # Transparências
    OVERLAY = "rgba(14, 18, 32, 0.9)"
    GLASS = "rgba(26, 35, 50, 0.8)"
    PARTICLE = "rgba(34, 211, 238, 0.1)"
    
    @classmethod
    def get_gradient(cls, color1: str, color2: str) -> str:
        """Cria um gradiente CSS."""
        return f"qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:1 {color2})"
    
    @classmethod
    def with_alpha(cls, color: str, alpha: float) -> str:
        """Adiciona transparência a uma cor."""
        if color.startswith("#"):
            color = color[1:]
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"