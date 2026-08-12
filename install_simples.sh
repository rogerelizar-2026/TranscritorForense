#!/bin/bash
# =============================================================================
# SCRIPT DE INSTALAÇÃO AUTOMÁTICA - TRANSCRITOR SIMPLIFICADO
# =============================================================================
# Instala dependências e configura o ambiente para uso imediato
# =============================================================================

set -e  # Sai em caso de erro

echo "=========================================="
echo "🎙️  Transcritor de Áudio Simplificado"
echo "=========================================="
echo ""

# Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION detectado"

# Verifica ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  ffmpeg não encontrado. Instalando..."
    
    if [ "$(uname)" == "Linux" ]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        fi
    elif [ "$(uname)" == "Darwin" ]; then
        if command -v brew &> /dev/null; then
            brew install ffmpeg
        else
            echo "❌ Homebrew não encontrado. Instale ffmpeg manualmente."
        fi
    else
        echo "⚠️  Instale ffmpeg manualmente: https://ffmpeg.org/download.html"
    fi
else
    echo "✅ ffmpeg já instalado"
fi

# Cria ambiente virtual (opcional, mas recomendado)
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Criando ambiente virtual..."
    python3 -m venv venv
    echo "✅ Ambiente virtual criado"
fi

# Ativa ambiente virtual
echo ""
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza pip
echo ""
echo "🔄 Atualizando pip..."
pip install --upgrade pip

# Instala dependências
echo ""
echo "📥 Instalando dependências (isso pode demorar)..."
pip install -r requirements_simples.txt

# Verifica token do Hugging Face
echo ""
echo "=========================================="
echo "🔑 Configuração do Hugging Face Token"
echo "=========================================="
echo ""
echo "Para usar a diarização (pyannote.audio), você precisa de um token:"
echo "1. Acesse: https://huggingface.co/settings/tokens"
echo "2. Crie um token com permissão 'read'"
echo "3. Execute: export HUGGINGFACE_TOKEN='seu_token_aqui'"
echo ""

# Oferece configuração do token
read -p "Deseja configurar seu token agora? (s/n): " CONFIGURE_TOKEN
if [ "$CONFIGURE_TOKEN" == "s" ] || [ "$CONFIGURE_TOKEN" == "S" ]; then
    read -sp "Digite seu token: " HF_TOKEN
    echo ""
    export HUGGINGFACE_TOKEN="$HF_TOKEN"
    echo "✅ Token configurado (sessão atual)"
    echo "   Para tornar permanente, adicione ao ~/.bashrc ou ~/.zshrc:"
    echo "   export HUGGINGFACE_TOKEN='seu_token_aqui'"
fi

# Testa instalação
echo ""
echo "=========================================="
echo "🧪 Testando instalação..."
echo "=========================================="
echo ""

python3 -c "import torch; print(f'✅ PyTorch {torch.__version__}')"
python3 -c "import torchaudio; print(f'✅ Torchaudio {torchaudio.__version__}')"

echo ""
echo "=========================================="
echo "✅ INSTALAÇÃO CONCLUÍDA!"
echo "=========================================="
echo ""
echo "Próximos passos:"
echo "1. Configure seu token do Hugging Face (obrigatório)"
echo "   export HUGGINGFACE_TOKEN='hf_seu_token_aqui'"
echo ""
echo "2. Teste com um arquivo de áudio:"
echo "   python src/transcriber_simples.py teste.mp3"
echo ""
echo "3. Veja todas as opções:"
echo "   python src/transcriber_simples.py --help"
echo ""
echo "📚 Documentação completa: README_SIMPLIFICADO.md"
echo ""
