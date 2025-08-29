# ⚛️ Nêutrons Optimizer

Um otimizador moderno e seguro para Windows 10/11 com interface inspirada em estruturas atômicas.

![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Plataforma](https://img.shields.io/badge/plataforma-Windows%2010%2F11-blue)
![Python](https://img.shields.io/badge/Python-3.10+-green)

## 🌟 Características

- **Interface Moderna**: Tema escuro inspirado em estruturas atômicas com partículas animadas
- **10 Otimizações Seguras**: Cada uma com simulação, aplicação e reversão
- **Sistema de Backup**: Backup automático antes de qualquer alteração
- **Elevação UAC**: Solicita privilégios automaticamente quando necessário
- **Logs Detalhados**: Sistema completo de logging para auditoria
- **Tema Nêutrons**: Paleta de cores ciano/azul com animações suaves

## 🎯 Otimizações Disponíveis

### 1. 🗑️ Limpeza de Arquivos Temporários
- Remove arquivos temporários seguros
- Limpa cache de navegadores (Chrome, Edge, Firefox)
- Mostra espaço liberado em tempo real

### 2. 🎮 Limpeza do Cache DirectX
- Remove cache de shaders DirectX
- Suporte para NVIDIA, AMD e Intel
- Resolve problemas gráficos comuns

### 3. 🚀 Gerenciador de Inicialização
- Lista e gerencia programas de startup
- Identifica itens seguros para desabilitar
- Backup automático das configurações

### 4. ⚡ Plano de Energia High Performance
- Ativa plano de alto desempenho
- Suporte ao Ultimate Performance (Windows 11)
- Restauração do plano anterior

### 5. 🎮 Game Mode e GPU Scheduling (HAGS)
- Ativa recursos para jogos
- Hardware Accelerated GPU Scheduling
- Compatível com Windows 10 20H1+

### 6. 🖼️ Limpeza do Cache de Miniaturas
- Remove cache de thumbnails
- Reinicia Explorer de forma segura
- Libera espaço significativo

### 7. 📦 Limpeza do Cache Windows Update
- Para serviços WU temporariamente
- Remove downloads antigos
- Reinicia serviços automaticamente

### 8. 💾 Otimização de Armazenamento
- TRIM automático para SSDs
- Análise segura para HDDs
- Detecção automática do tipo de disco

### 9. 🌐 Reset de Rede
- Flush DNS e reset Winsock
- Resolve problemas de conectividade
- Requer reinicialização

### 10. 🎯 Desabilitar Xbox Game Bar
- Remove Xbox Game Bar e DVR
- Melhora performance em jogos
- Completamente reversível

## 🔧 Requisitos do Sistema

- **SO**: Windows 10 (build 10240+) ou Windows 11
- **Python**: 3.10 ou superior
- **RAM**: Mínimo 4GB
- **Espaço**: 500MB livres
- **Privilégios**: Administrador (recomendado)

## 📦 Instalação

### Método 1: Executável Compilado
1. Baixe o `NeutronsOptimizerSetup.exe`
2. Execute como administrador
3. Siga o assistente de instalação

### Método 2: Código Fonte
```bash
# Clone o repositório
git clone https://github.com/MusashiSanS2/neutrons-optimizer.git
cd neutrons-optimizer

# Instale dependências
pip install -r requirements.txt

# Execute em modo desenvolvimento
python run_dev.py
```

## 🚀 Como Usar

### Primeira Execução
1. **Execute como Administrador** para funcionalidade completa
2. **Crie um Ponto de Restauração** (recomendado)
3. **Simule** as otimizações antes de aplicar
4. **Aplique** uma otimização por vez

### Interface Principal
- **Dashboard**: Informações do sistema em tempo real
- **Otimizações**: Cards com simular/aplicar/desfazer
- **Logs**: Histórico detalhado de operações
- **Sobre**: Informações e créditos

### Fluxo Recomendado
```
1. Dashboard → Verificar sistema
2. Criar Ponto de Restauração
3. Simular otimização
4. Aplicar se satisfeito
5. Verificar logs
6. Repetir para outras otimizações
```

## 🛡️ Segurança

### Sistema de Backup
- **Registro**: Export .reg antes de alterações
- **Arquivos**: Cópia de segurança automática
- **Serviços**: Estado original salvo
- **Configurações**: Backup completo

### Verificações de Segurança
- Validação de ambiente antes de executar
- Detecção de processos críticos
- Verificação de espaço em disco
- Timeout em operações longas

### Reversão
Todas as otimizações podem ser revertidas:
```
Botão "Desfazer" → Restaura estado anterior
```

## 🔨 Desenvolvimento

### Estrutura do Projeto
```
neutrons-optimizer/
├── src/
│   ├── app.py              # Aplicação principal
│   ├── core/               # Lógica principal
│   │   ├── optimizations/  # 10 otimizações
│   │   ├── safety/         # Backup e restore
│   │   └── system/         # Sistema (UAC, registro, etc)
│   ├── ui/                 # Interface gráfica
│   │   ├── components/     # Componentes UI
│   │   ├── theme/          # Tema e estilos
│   │   └── main_window.py  # Janela principal
│   └── utils/              # Utilitários
├── tests/                  # Testes
├── build/                  # Build e assets
├── run_dev.py             # Executar desenvolvimento
├── build.py               # Script de build
└── requirements.txt       # Dependências
```

### Executar Testes
```bash
# Testes de fumaça
python tests/smoke_tests.py

# Verificar todas as funcionalidades básicas
```

### Build para Produção
```bash
# Compilar executável
python build.py

# Resultado em dist/NeutronsOptimizer.exe
```

## 🎨 Tema Nêutrons

### Paleta de Cores
- **Base**: `#0e1220` (Fundo escuro)
- **Superfície**: `#1a2332` (Cards)
- **Primário**: `#22d3ee` (Cyan brilhante)
- **Secundário**: `#60a5fa` (Azul médio)
- **Acento**: `#8b5cf6` (Roxo discreto)

### Elementos Visuais
- **Partículas Animadas**: Orbitando em baixa opacidade
- **Núcleo Central**: Representação atômica sutil
- **Microanimações**: Feedback visual suave
- **Gradientes**: Transições suaves entre cores

## 📋 Logs e Auditoria

### Localização dos Logs
```
%LOCALAPPDATA%/NeutronsOptimizer/logs/optimizer.log
```

### Informações Registradas
- Início/fim de operações
- Resultados detalhados
- Erros e warnings
- Alterações no sistema
- Backups criados

### Backups
```
%LOCALAPPDATA%/NeutronsOptimizer/backups/
├── registry/    # Exports .reg
├── files/       # Arquivos copiados
├── services/    # Estados de serviços
└── power/       # Configurações de energia
```

## ❓ Solução de Problemas

### Problemas Comuns

**"Privilégios insuficientes"**
- Execute como administrador
- Verifique UAC ativado

**"Otimização falhou"**
- Verifique logs para detalhes
- Tente reverter e aplicar novamente
- Verifique espaço em disco

**"Interface não carrega"**
- Verifique dependências instaladas
- Execute `python run_dev.py` para debug

### Recuperação de Emergência

**Reverter todas as alterações:**
1. Use "Restauração do Sistema" do Windows
2. Selecione ponto criado antes das otimizações

**Problemas de boot:**
1. Boot em Modo Seguro
2. Execute `sfc /scannow`
3. Use ponto de restauração

## 🤝 Contribuindo

### Como Contribuir
1. Fork o projeto
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

### Desenvolvendo Novas Otimizações
```python
from core.optimizations.base import BaseOptimization, OptimizationResult

class MinhaOptimizacao(BaseOptimization):
    @property
    def display_name(self) -> str:
        return "Minha Otimização"
    
    def simulate(self) -> OptimizationResult:
        # Simular mudanças
        return OptimizationResult(True, "Simulação OK")
    
    def apply(self) -> OptimizationResult:
        # Aplicar mudanças
        return OptimizationResult(True, "Aplicado")
    
    def revert(self) -> OptimizationResult:
        # Reverter mudanças
        return OptimizationResult(True, "Revertido")
```

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## 👨‍💻 Créditos

**Desenvolvido por MusashiSanS2**
- Interface moderna inspirada em estruturas atômicas
- Sistema de otimizações seguras e reversíveis
- Tema visual único com animações de partículas

---

## 📞 Suporte

Para problemas, sugestões ou contribuições:
- 🐛 **Issues**: [GitHub Issues](https://github.com/MusashiSanS2/neutrons-optimizer/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/MusashiSanS2/neutrons-optimizer/discussions)

---

⚛️ **Nêutrons Optimizer** - Otimização segura com estilo moderno!