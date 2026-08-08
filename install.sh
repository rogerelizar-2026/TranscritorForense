#!/bin/bash
# =============================================================================
# INSTALADOR AUTOMÁTICO - TRANSCRITOR FORENSE DE ÁUDIO
# =============================================================================
# Este script automatiza toda a instalação do sistema, deixando-o pronto para uso.
# Compatível com Linux e macOS
# Versão: 2.0.0 (Corrigida e Otimizada)
# =============================================================================

set -e  # Sai em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funções de log
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCESSO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[ATENÇÃO]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

log_step() {
    echo -e "${CYAN}[PASSO]${NC} $1"
}

# Cabeçalho
echo ""
echo "============================================================================="
echo "  ⚖️  INSTALADOR AUTOMÁTICO - TRANSCRITOR FORENSE DE ÁUDIO"
echo "     Versão 2.0.0 - Compatível com Python 3.10 a 3.12"
echo "============================================================================="
echo ""
log_info "Este instalador configurará todo o ambiente necessário para uso do sistema."
echo ""

# Verificar se está na pasta correta
if [ ! -f "requirements.txt" ] || [ ! -f "config.yaml" ]; then
    log_error "Execute este script no diretório raiz do projeto (onde estão requirements.txt e config.yaml)"
    exit 1
fi

# Passo 1: Verificar Python
log_step "1/8: Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    log_error "Python não encontrado. Instale Python 3.10 ou superior."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
log_info "Python encontrado: $PYTHON_VERSION"

# Verificar versão mínima (3.10)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1 | sed 's/v//')
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
    log_error "Python 3.10 ou superior é necessário. Versão atual: $PYTHON_VERSION"
    exit 1
fi

# Verificar versão máxima (3.12)
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -gt 12 ]; then
    log_warning "Python > 3.12 detectado. Algumas bibliotecas podem ter incompatibilidades."
fi

log_success "Python OK ✓"
echo ""

# Passo 2: Verificar Git
log_step "2/8: Verificando Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    log_info "$GIT_VERSION"
    log_success "Git OK ✓"
else
    log_warning "Git não encontrado. Algumas funcionalidades podem não estar disponíveis."
fi
echo ""

# Passo 3: Criar ambiente virtual
log_step "3/8: Criando ambiente virtual..."
if [ -d "venv" ]; then
    log_warning "Ambiente virtual já existe. Removendo..."
    rm -rf venv
fi

$PYTHON_CMD -m venv venv
log_success "Ambiente virtual criado ✓"
echo ""

# Passo 4: Ativar ambiente virtual e atualizar pip
log_step "4/8: Ativando ambiente e atualizando pip..."
source venv/bin/activate
pip install --upgrade pip setuptools wheel --quiet
log_success "Pip e ferramentas atualizadas ✓"
echo ""

# Passo 5: Instalar dependências do sistema (Linux apenas)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    log_step "5/8: Instalando dependências do sistema (Linux)..."
    
    if command -v apt-get &> /dev/null; then
        log_info "Detectado Debian/Ubuntu. Instalando pacotes..."
        sudo apt-get update -qq
        sudo apt-get install -y -qq ffmpeg libsndfile1 portaudio19-dev espeak-ng
        log_success "Dependências do sistema instaladas ✓"
    elif command -v dnf &> /dev/null; then
        log_info "Detectado Fedora/RHEL. Instalando pacotes..."
        sudo dnf install -y -q ffmpeg libsndfile portaudio-devel espeak-ng
        log_success "Dependências do sistema instaladas ✓"
    elif command -v pacman &> /dev/null; then
        log_info "Detectado Arch Linux. Instalando pacotes..."
        sudo pacman -S --noconfirm --quiet ffmpeg libsndfile portaudio espeak-ng
        log_success "Dependências do sistema instaladas ✓"
    else
        log_warning "Gerenciador de pacotes não detectado. Pode ser necessário instalar dependências manualmente."
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    log_step "5/8: Verificando dependências do sistema (macOS)..."
    if command -v brew &> /dev/null; then
        log_info "Homebrew detectado. Verificando ffmpeg..."
        if brew list ffmpeg &> /dev/null; then
            log_info "ffmpeg já instalado"
        else
            log_info "Instalando ffmpeg..."
            brew install ffmpeg
        fi
        log_success "Dependências do sistema verificadas ✓"
    else
        log_warning "Homebrew não encontrado. Recomenda-se instalar: https://brew.sh"
    fi
else
    log_step "5/8: Pulando dependências do sistema (SO não identificado como Linux/macOS)"
fi
echo ""

# Passo 6: Instalar dependências Python
log_step "6/8: Instalando dependências Python (pode demorar 5-15 minutos)..."
log_info "Instalando PyTorch primeiro (biblioteca principal)..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet

log_info "Instalando Hugging Face Hub com versão compatível..."
pip install "huggingface_hub>=0.20.0,<0.26.0" --quiet

log_info "Instalando demais dependências..."
pip install -r requirements.txt --quiet

log_success "Dependências Python instaladas ✓"
echo ""

# Passo 7: Criar diretórios necessários
log_step "7/8: Criando estrutura de diretórios..."
mkdir -p output samples models templates
log_success "Diretórios criados ✓"
echo ""

# Passo 8: Configurar token Hugging Face
log_step "8/8: Configurando token Hugging Face..."
echo ""
echo "============================================================================="
echo "  CONFIGURAÇÃO DO HUGGING FACE"
echo "============================================================================="
echo ""
log_info "Os modelos pyannote.audio exigem um token do Hugging Face (gratuito)."
echo ""
log_info "Siga estas instruções:"
echo "  1. Acesse: https://huggingface.co/join (crie conta se não tiver)"
echo "  2. Aceite os termos dos modelos:"
echo "     - https://huggingface.co/pyannote/speaker-diarization-3.1"
echo "     - https://huggingface.co/pyannote/segmentation-3.0"
echo "  3. Gere um token em: https://huggingface.co/settings/tokens"
echo "  4. Copie o token (começa com 'hf_')"
echo ""

read -p "Cole seu token do Hugging Face aqui: " HF_TOKEN

if [ -z "$HF_TOKEN" ]; then
    log_warning "Token não fornecido. O sistema não funcionará sem ele."
    log_info "Você pode configurar manualmente depois editando config.yaml"
else
    # Atualizar config.yaml com o token
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i.bak "s/huggingface_token: \"hf_seu_token_aqui\"/huggingface_token: \"$HF_TOKEN\"/" config.yaml
        rm -f config.yaml.bak
    else
        sed -i "s/huggingface_token: \"hf_seu_token_aqui\"/huggingface_token: \"$HF_TOKEN\"/" config.yaml
    fi
    log_success "Token configurado em config.yaml ✓"
fi
echo ""

# Resumo final
echo "============================================================================="
echo "  INSTALAÇÃO CONCLUÍDA!"
echo "============================================================================="
echo ""
log_success "O sistema está pronto para uso!"
echo ""
echo "Próximos passos:"
echo "  1. Ative o ambiente virtual:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Execute a aplicação:"
echo "     python -m src.app"
echo ""
echo "  3. Acesse no navegador: http://localhost:7860"
echo ""
echo "Ou execute o script de inicialização rápida:"
echo "  ./iniciar.sh"
echo ""
echo "============================================================================="
echo ""

# Criar script de inicialização
cat > iniciar.sh << 'EOF'
#!/bin/bash
# Script de inicialização rápida

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d "venv" ]; then
    echo "Erro: Ambiente virtual não encontrado. Execute install.sh primeiro."
    exit 1
fi

source venv/bin/activate
python -m src.app
EOF

chmod +x iniciar.sh
log_success "Script de inicialização criado: iniciar.sh"

echo ""
