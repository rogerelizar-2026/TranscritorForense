# 📋 Instruções de Instalação Corrigida - Transcritor Forense de Áudio

## ✅ Correções Implementadas (Versão 2.0.0)

### Problemas Resolvidos:
1. **Conflitos de Versão do NumPy**: Removida restrição `numpy<2.0.0` que causava incompatibilidade
2. **Versões Desatualizadas**: Atualizadas todas as dependências para versões compatíveis com Python 3.10-3.12
3. **Torch/Torchaudio Mismatch**: Garantido que torch e torchaudio tenham versões compatíveis
4. **Instalação do PyTorch**: Separação da instalação do PyTorch para evitar conflitos
5. **Dependências do Sistema**: Adicionado `espeak-ng` para suporte a processamento de voz

### Dependências Atualizadas:
| Pacote | Versão Antiga | Nova Versão |
|--------|--------------|-------------|
| torch | 2.1.0 | >=2.3.0,<2.8.0 |
| torchaudio | 2.1.0 | >=2.3.0,<2.8.0 |
| pyannote.audio | 3.1.1 | >=3.3.0,<4.1.0 |
| whisperx | 3.1.1 | >=3.3.0,<3.9.0 |
| speechbrain | 1.0.0 | >=1.0.0,<1.2.0 |
| gradio | 4.31.0 | >=4.31.0,<6.0.0 |
| librosa | 0.10.1 | >=0.10.1,<0.12.0 |
| soundfile | 0.12.1 | >=0.12.1,<0.15.0 |
| numpy | <2.0.0 | >=1.24.0,<3.0.0 |

---

## 🐧 Linux/macOS

### Pré-requisitos:
- Python 3.10 a 3.12
- Git (opcional, mas recomendado)
- Acesso à internet para download dos modelos

### Passo a Passo:

```bash
# 1. Navegue até o diretório do projeto
cd /caminho/para/projeto

# 2. Execute o instalador automático
chmod +x install.sh
./install.sh

# 3. Siga as instruções na tela para configurar o token do Hugging Face
```

### Instalação Manual (Alternativa):

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Atualizar pip e ferramentas
pip install --upgrade pip setuptools wheel

# Instalar PyTorch primeiro
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# Instalar demais dependências
pip install -r requirements.txt

# Instalar dependências do sistema (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y ffmpeg libsndfile1 portaudio19-dev espeak-ng
```

---

## 🪟 Windows

### Pré-requisitos:
- Python 3.10 a 3.12 (marcar "Add Python to PATH" na instalação)
- PowerShell disponível

### Passo a Passo:

```batch
REM 1. Abra o Prompt de Comando como Administrador
REM 2. Navegue até o diretório do projeto
cd C:\caminho\para\projeto

REM 3. Execute o instalador
install.bat

REM 4. Siga as instruções na tela
```

### Instalação Manual (Alternativa):

```batch
REM Criar ambiente virtual
python -m venv venv

REM Ativar ambiente
call venv\Scripts\activate

REM Atualizar pip
python -m pip install --upgrade pip setuptools wheel

REM Instalar PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

REM Instalar demais dependências
pip install -r requirements.txt
```

### Instalando FFmpeg no Windows:
1. Baixe de: https://www.gyan.dev/ffmpeg/builds/
2. Extraia o arquivo ZIP
3. Copie a pasta `bin` para `C:\ffmpeg\bin`
4. Adicione `C:\ffmpeg\bin` ao PATH:
   - Painel de Controle → Sistema → Configurações Avançadas → Variáveis de Ambiente
   - Edite a variável `Path` e adicione o caminho

---

## 🔑 Configuração do Hugging Face (Obrigatório)

Os modelos `pyannote.audio` exigem autenticação:

1. **Crie uma conta**: https://huggingface.co/join
2. **Aceite os termos** dos modelos:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. **Gere um token** em: https://huggingface.co/settings/tokens
4. **Copie o token** (começa com `hf_`)
5. **Configure** durante a instalação ou edite `config.yaml` manualmente

---

## 🚀 Executando a Aplicação

### Linux/macOS:
```bash
# Usando o script de inicialização
./iniciar.sh

# Ou manualmente
source venv/bin/activate
python -m src.app
```

### Windows:
```batch
REM Usando o script de inicialização
iniciar.bat

REM Ou manualmente
call venv\Scripts\activate
python -m src.app
```

### Acessando a Interface:
Abra no navegador: http://localhost:7860

---

## 📁 Estrutura de Diretórios Criada

```
projeto/
├── venv/           # Ambiente virtual Python
├── src/            # Código fonte
├── output/         # Transcrições geradas
├── samples/        # Amostras de referência
├── models/         # Modelos baixados
├── templates/      # Templates de relatório
├── config.yaml     # Configuração
├── requirements.txt
├── install.sh      # Instalador Linux/macOS
└── install.bat     # Instalador Windows
```

---

## ⚠️ Solução de Problemas

### Erro: "Python não encontrado"
- **Linux/macOS**: `sudo apt-get install python3 python3-venv`
- **Windows**: Reinstale Python marcando "Add to PATH"

### Erro: "FFmpeg não encontrado"
- **Linux**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Siga instruções acima

### Erro: "No module named 'pyannote'"
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Erro: "CUDA out of memory"
O sistema funciona sem GPU. Para forçar modo CPU:
```python
# Em src/app.py, altere:
device = "cpu"  # em vez de "cuda"
```

### Erro: "Token inválido"
- Verifique se aceitou os termos dos modelos pyannote
- Gere um novo token em: https://huggingface.co/settings/tokens
- Atualize o `config.yaml`

---

## 📞 Suporte

Para mais informações, consulte:
- `README.md` - Visão geral do projeto
- `MANUAL_USUARIO.md` - Guia completo do usuário
- `GUIA_INSTALACAO_WINDOWS_INICIANTES.md` - Guia específico para Windows

---

**Versão do Instalador**: 2.0.0  
**Última Atualização**: 2024  
**Compatibilidade**: Python 3.10 - 3.12
