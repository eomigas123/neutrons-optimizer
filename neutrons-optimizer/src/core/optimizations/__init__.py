"""
Módulo de otimizações do Nêutrons Optimizer.
"""
from .temp_cleanup import TempCleanupOptimization
from .dx_shader_cache import DirectXShaderCacheOptimization
from .startup_manager import StartupManagerOptimization
from .power_plan import PowerPlanOptimization
from .game_features import GameFeaturesOptimization
from .thumbnails_cache import ThumbnailsCacheOptimization
from .wu_cache import WindowsUpdateCacheOptimization
from .storage_trim import StorageTrimOptimization
from .network_reset import NetworkResetOptimization
from .xbox_gamebar import XboxGameBarOptimization

# Lista de todas as otimizações disponíveis
OPTIMIZATIONS = [
    TempCleanupOptimization,
    DirectXShaderCacheOptimization,
    StartupManagerOptimization,
    PowerPlanOptimization,
    GameFeaturesOptimization,
    ThumbnailsCacheOptimization,
    WindowsUpdateCacheOptimization,
    StorageTrimOptimization,
    NetworkResetOptimization,
    XboxGameBarOptimization
]

__all__ = [
    'TempCleanupOptimization',
    'DirectXShaderCacheOptimization', 
    'StartupManagerOptimization',
    'PowerPlanOptimization',
    'GameFeaturesOptimization',
    'ThumbnailsCacheOptimization',
    'WindowsUpdateCacheOptimization',
    'StorageTrimOptimization',
    'NetworkResetOptimization',
    'XboxGameBarOptimization',
    'OPTIMIZATIONS'
]