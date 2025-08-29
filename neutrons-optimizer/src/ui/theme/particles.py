"""
Sistema de partículas animadas para o tema Nêutrons.
"""
import math
import random
from typing import List, Tuple
from PySide6.QtCore import QTimer, QPropertyAnimation, QEasingCurve, QPoint, QRect
from PySide6.QtGui import QPainter, QPen, QBrush, QColor
from PySide6.QtWidgets import QWidget
from .colors import NeutronColors as NC


class Particle:
    """Representa uma partícula individual."""
    
    def __init__(self, x: float, y: float, radius: float = 2.0):
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = random.uniform(0, 2 * math.pi)
        self.speed = random.uniform(0.5, 2.0)
        self.orbit_radius = random.uniform(50, 150)
        self.orbit_speed = random.uniform(0.01, 0.03)
        self.opacity = random.uniform(0.1, 0.3)
        self.color = self._get_particle_color()
        
    def _get_particle_color(self) -> QColor:
        """Retorna uma cor aleatória para a partícula."""
        colors = [NC.PRIMARY, NC.SECONDARY, NC.ACCENT]
        base_color = QColor(random.choice(colors))
        base_color.setAlphaF(self.opacity)
        return base_color
    
    def update(self, center_x: float, center_y: float, dt: float):
        """Atualiza a posição da partícula."""
        # Movimento orbital ao redor do centro
        self.angle += self.orbit_speed * dt
        
        # Posição orbital
        orbit_x = center_x + math.cos(self.angle) * self.orbit_radius
        orbit_y = center_y + math.sin(self.angle) * self.orbit_radius
        
        # Movimento suave em direção à posição orbital
        dx = orbit_x - self.x
        dy = orbit_y - self.y
        
        self.x += dx * 0.02 * dt
        self.y += dy * 0.02 * dt
        
        # Adicionar um pouco de flutuação
        self.x += math.sin(self.angle * 2) * 0.5
        self.y += math.cos(self.angle * 2) * 0.5


class ParticleSystem(QWidget):
    """Sistema de partículas para animação de fundo."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles: List[Particle] = []
        self.nucleus_particles: List[Particle] = []
        self.last_time = 0
        
        # Timer para animação
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(16)  # ~60 FPS
        
        # Configuração
        self.setMouseTracking(False)
        self.setAttribute(81)  # WA_TransparentForMouseEvents
        
        self._create_particles()
    
    def _create_particles(self):
        """Cria as partículas iniciais."""
        # Partículas orbitais
        for _ in range(20):
            x = random.uniform(0, self.width() or 800)
            y = random.uniform(0, self.height() or 600)
            radius = random.uniform(1, 3)
            self.particles.append(Particle(x, y, radius))
        
        # Partículas do núcleo (centro)
        for _ in range(5):
            x = (self.width() or 800) / 2
            y = (self.height() or 600) / 2
            radius = random.uniform(2, 4)
            particle = Particle(x, y, radius)
            particle.orbit_radius = random.uniform(10, 30)
            particle.orbit_speed = random.uniform(0.05, 0.1)
            particle.opacity = random.uniform(0.3, 0.6)
            particle.color = QColor(NC.PRIMARY)
            particle.color.setAlphaF(particle.opacity)
            self.nucleus_particles.append(particle)
    
    def update_particles(self):
        """Atualiza todas as partículas."""
        import time
        current_time = time.time() * 1000
        
        if self.last_time == 0:
            self.last_time = current_time
            return
        
        dt = current_time - self.last_time
        self.last_time = current_time
        
        # Centro da tela
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Atualizar partículas orbitais
        for particle in self.particles:
            particle.update(center_x, center_y, dt)
        
        # Atualizar partículas do núcleo
        for particle in self.nucleus_particles:
            particle.update(center_x, center_y, dt)
        
        self.update()  # Redesenhar
    
    def paintEvent(self, event):
        """Desenha as partículas."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Desenhar conexões entre partículas próximas
        self._draw_connections(painter)
        
        # Desenhar partículas orbitais
        for particle in self.particles:
            self._draw_particle(painter, particle)
        
        # Desenhar núcleo
        self._draw_nucleus(painter)
        
        # Desenhar partículas do núcleo
        for particle in self.nucleus_particles:
            self._draw_particle(painter, particle, glow=True)
    
    def _draw_particle(self, painter: QPainter, particle: Particle, glow: bool = False):
        """Desenha uma partícula individual."""
        # Configurar cor e pincel
        color = particle.color
        
        if glow:
            # Efeito de brilho para partículas do núcleo
            glow_color = QColor(color)
            glow_color.setAlphaF(0.1)
            
            # Desenhar várias camadas para efeito de brilho
            for i in range(3):
                radius = particle.radius + i * 2
                glow_color.setAlphaF(0.1 / (i + 1))
                painter.setBrush(QBrush(glow_color))
                painter.setPen(QPen(glow_color, 0))
                painter.drawEllipse(
                    int(particle.x - radius),
                    int(particle.y - radius),
                    int(radius * 2),
                    int(radius * 2)
                )
        
        # Desenhar partícula principal
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color, 0))
        painter.drawEllipse(
            int(particle.x - particle.radius),
            int(particle.y - particle.radius),
            int(particle.radius * 2),
            int(particle.radius * 2)
        )
    
    def _draw_nucleus(self, painter: QPainter):
        """Desenha o núcleo central."""
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Núcleo principal
        nucleus_color = QColor(NC.PRIMARY)
        nucleus_color.setAlphaF(0.4)
        
        painter.setBrush(QBrush(nucleus_color))
        painter.setPen(QPen(nucleus_color, 2))
        painter.drawEllipse(
            int(center_x - 8),
            int(center_y - 8),
            16,
            16
        )
        
        # Anel externo
        ring_color = QColor(NC.SECONDARY)
        ring_color.setAlphaF(0.2)
        painter.setBrush(QBrush())
        painter.setPen(QPen(ring_color, 1))
        painter.drawEllipse(
            int(center_x - 25),
            int(center_y - 25),
            50,
            50
        )
    
    def _draw_connections(self, painter: QPainter):
        """Desenha linhas de conexão entre partículas próximas."""
        connection_color = QColor(NC.PRIMARY)
        connection_color.setAlphaF(0.1)
        painter.setPen(QPen(connection_color, 1))
        
        # Verificar distância entre partículas
        for i, particle1 in enumerate(self.particles):
            for particle2 in self.particles[i + 1:]:
                dx = particle1.x - particle2.x
                dy = particle1.y - particle2.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Desenhar linha se as partículas estão próximas
                if distance < 100:
                    alpha = 1.0 - (distance / 100)
                    connection_color.setAlphaF(alpha * 0.1)
                    painter.setPen(QPen(connection_color, 1))
                    painter.drawLine(
                        int(particle1.x), int(particle1.y),
                        int(particle2.x), int(particle2.y)
                    )
    
    def resizeEvent(self, event):
        """Reposiciona partículas quando a janela é redimensionada."""
        super().resizeEvent(event)
        
        # Recriar partículas para o novo tamanho
        if self.particles:
            self.particles.clear()
            self.nucleus_particles.clear()
            self._create_particles()


class AnimatedBackground(QWidget):
    """Widget de fundo animado combinando partículas e gradientes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particle_system = ParticleSystem(self)
        
        # Configurar widget
        self.setAttribute(81)  # WA_TransparentForMouseEvents
        self.setStyleSheet(f"""
            background: {NC.get_gradient(NC.BACKGROUND, NC.SURFACE)};
        """)
    
    def resizeEvent(self, event):
        """Redimensiona o sistema de partículas."""
        super().resizeEvent(event)
        if hasattr(self, 'particle_system'):
            self.particle_system.resize(self.size())