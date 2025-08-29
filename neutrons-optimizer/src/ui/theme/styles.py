"""
Estilos CSS para o tema Nêutrons.
"""
from .colors import NeutronColors as NC


class NeutronStyles:
    """Estilos CSS do tema Nêutrons."""
    
    @staticmethod
    def get_main_stylesheet() -> str:
        """Retorna o stylesheet principal."""
        return f"""
        /* Estilo base da aplicação */
        QMainWindow {{
            background-color: {NC.BACKGROUND};
            color: {NC.TEXT_PRIMARY};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }}
        
        /* Widget base */
        QWidget {{
            background-color: transparent;
            color: {NC.TEXT_PRIMARY};
            border: none;
        }}
        
        /* Painéis principais */
        .MainPanel {{
            background-color: {NC.SURFACE};
            border-radius: 12px;
            border: 1px solid {NC.BORDER};
        }}
        
        .CardPanel {{
            background-color: {NC.SURFACE_VARIANT};
            border-radius: 8px;
            border: 1px solid {NC.BORDER};
            padding: 16px;
            margin: 8px;
        }}
        
        /* Botões principais */
        QPushButton {{
            background-color: {NC.PRIMARY};
            color: {NC.BACKGROUND};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 9pt;
        }}
        
        QPushButton:hover {{
            background-color: {NC.SECONDARY};
            transform: translateY(-1px);
        }}
        
        QPushButton:pressed {{
            background-color: {NC.ACCENT};
            transform: translateY(0px);
        }}
        
        QPushButton:disabled {{
            background-color: {NC.TEXT_DISABLED};
            color: {NC.TEXT_MUTED};
        }}
        
        /* Botões secundários */
        .SecondaryButton {{
            background-color: transparent;
            color: {NC.PRIMARY};
            border: 1px solid {NC.PRIMARY};
        }}
        
        .SecondaryButton:hover {{
            background-color: {NC.with_alpha(NC.PRIMARY, 0.1)};
        }}
        
        /* Botão de perigo */
        .DangerButton {{
            background-color: {NC.ERROR};
            color: white;
        }}
        
        .DangerButton:hover {{
            background-color: #dc2626;
        }}
        
        /* Botão de sucesso */
        .SuccessButton {{
            background-color: {NC.SUCCESS};
            color: white;
        }}
        
        .SuccessButton:hover {{
            background-color: #059669;
        }}
        
        /* Labels */
        QLabel {{
            color: {NC.TEXT_PRIMARY};
            background-color: transparent;
        }}
        
        .TitleLabel {{
            font-size: 18pt;
            font-weight: bold;
            color: {NC.PRIMARY};
            margin: 16px 0px;
        }}
        
        .SubtitleLabel {{
            font-size: 12pt;
            font-weight: 600;
            color: {NC.TEXT_SECONDARY};
            margin: 8px 0px;
        }}
        
        .MutedLabel {{
            color: {NC.TEXT_MUTED};
            font-size: 9pt;
        }}
        
        /* Progress Bar */
        QProgressBar {{
            background-color: {NC.SURFACE_VARIANT};
            border: 1px solid {NC.BORDER};
            border-radius: 4px;
            text-align: center;
            color: {NC.TEXT_PRIMARY};
            font-weight: bold;
        }}
        
        QProgressBar::chunk {{
            background: {NC.get_gradient(NC.PRIMARY, NC.SECONDARY)};
            border-radius: 3px;
        }}
        
        /* ScrollArea */
        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        
        QScrollBar:vertical {{
            background-color: {NC.SURFACE_VARIANT};
            width: 12px;
            border-radius: 6px;
            margin: 0px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {NC.PRIMARY};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {NC.SECONDARY};
        }}
        
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            background-color: {NC.SURFACE};
            border: 1px solid {NC.BORDER};
            border-radius: 8px;
        }}
        
        QTabBar::tab {{
            background-color: {NC.SURFACE_VARIANT};
            color: {NC.TEXT_SECONDARY};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {NC.PRIMARY};
            color: {NC.BACKGROUND};
            font-weight: bold;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {NC.HOVER};
            color: {NC.TEXT_PRIMARY};
        }}
        
        /* List Widget */
        QListWidget {{
            background-color: {NC.SURFACE_VARIANT};
            border: 1px solid {NC.BORDER};
            border-radius: 6px;
            alternate-background-color: {NC.SURFACE};
        }}
        
        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {NC.DIVIDER};
        }}
        
        QListWidget::item:selected {{
            background-color: {NC.PRIMARY};
            color: {NC.BACKGROUND};
        }}
        
        QListWidget::item:hover {{
            background-color: {NC.HOVER};
        }}
        
        /* Tooltips */
        QToolTip {{
            background-color: {NC.SURFACE_VARIANT};
            color: {NC.TEXT_PRIMARY};
            border: 1px solid {NC.BORDER};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 9pt;
        }}
        
        /* Menu */
        QMenu {{
            background-color: {NC.SURFACE_VARIANT};
            border: 1px solid {NC.BORDER};
            border-radius: 6px;
            padding: 4px;
        }}
        
        QMenu::item {{
            background-color: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QMenu::item:selected {{
            background-color: {NC.PRIMARY};
            color: {NC.BACKGROUND};
        }}
        
        /* Splitter */
        QSplitter::handle {{
            background-color: {NC.BORDER};
        }}
        
        QSplitter::handle:horizontal {{
            width: 2px;
        }}
        
        QSplitter::handle:vertical {{
            height: 2px;
        }}
        
        /* Text Edit */
        QTextEdit, QPlainTextEdit {{
            background-color: {NC.SURFACE_VARIANT};
            color: {NC.TEXT_PRIMARY};
            border: 1px solid {NC.BORDER};
            border-radius: 6px;
            padding: 8px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 9pt;
        }}
        
        /* Status indicators */
        .StatusSuccess {{
            color: {NC.SUCCESS};
            font-weight: bold;
        }}
        
        .StatusWarning {{
            color: {NC.WARNING};
            font-weight: bold;
        }}
        
        .StatusError {{
            color: {NC.ERROR};
            font-weight: bold;
        }}
        
        .StatusInfo {{
            color: {NC.INFO};
            font-weight: bold;
        }}
        
        /* Animações CSS */
        QPushButton {{
            transition: all 0.2s ease;
        }}
        
        .CardPanel:hover {{
            border-color: {NC.PRIMARY};
            box-shadow: 0 4px 12px {NC.with_alpha(NC.PRIMARY, 0.2)};
        }}
        """
    
    @staticmethod
    def get_card_style(status: str = "default") -> str:
        """Retorna estilo para cards baseado no status."""
        status_colors = {
            "success": NC.SUCCESS,
            "warning": NC.WARNING,
            "error": NC.ERROR,
            "info": NC.INFO,
            "default": NC.BORDER
        }
        
        border_color = status_colors.get(status, NC.BORDER)
        
        return f"""
        QFrame {{
            background-color: {NC.SURFACE_VARIANT};
            border: 2px solid {border_color};
            border-radius: 8px;
            padding: 16px;
            margin: 4px;
        }}
        """
    
    @staticmethod
    def get_button_style(variant: str = "primary") -> str:
        """Retorna estilo para botões baseado na variante."""
        styles = {
            "primary": f"""
                QPushButton {{
                    background-color: {NC.PRIMARY};
                    color: {NC.BACKGROUND};
                }}
                QPushButton:hover {{
                    background-color: {NC.SECONDARY};
                }}
            """,
            "secondary": f"""
                QPushButton {{
                    background-color: transparent;
                    color: {NC.PRIMARY};
                    border: 1px solid {NC.PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {NC.with_alpha(NC.PRIMARY, 0.1)};
                }}
            """,
            "success": f"""
                QPushButton {{
                    background-color: {NC.SUCCESS};
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #059669;
                }}
            """,
            "danger": f"""
                QPushButton {{
                    background-color: {NC.ERROR};
                    color: white;
                }}
                QPushButton:hover {{
                    background-color: #dc2626;
                }}
            """
        }
        
        return styles.get(variant, styles["primary"])