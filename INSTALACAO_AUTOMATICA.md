# 🚀 Guia de Instalação Automática

Este documento descreve como usar os scripts instaladores automáticos do **Transcritor Forense de Áudio**.

---

## 📋 Visão Geral

Foram criados dois scripts instaladores que automatizam **todo o processo de instalação**, deixando o sistema pronto para uso:

| Script | Sistema Operacional | Arquivo |
|--------|---------------------|---------|
| **Linux/macOS** | Linux, macOS, WSL | `install.sh` |
| **Windows** | Windows 10/11 | `install.bat` |

---

## ⚡ Instalação Rápida

### Linux/macOS

```bash
# 1. Torne o script executável (apenas na primeira vez)
chmod +x install.sh

# 2. Execute o instalador
./install.sh

# 3. Após a instalação, inicie o sistema
./iniciar.sh
```

### Windows

```cmd
REM 1. Execute o instalador (clique duplo ou no prompt)
install.bat

REM 2. Após a instalação, inicie o sistema
iniciar.bat
```

---

## 🔍 O Que o Instalador Faz

Ambos os scripts realizam automaticamente as seguintes etapas:

### Passo 1: Verificação de Pré-requisitos
- ✅ Verifica se Python 3.10+ está instalado
- ✅ Verifica se Git está disponível (opcional)
- ✅ Valida que está sendo executado no diretório correto

### Passo 2: Criação do Ambiente Virtual
- ✅ Cria um ambiente virtual isolado (`venv/`)
- ✅ Ativa o ambiente
- ✅ Atualiza o `pip` para a versão mais recente

### Passo 3: Dependências do Sistema
**Linux:**
- ✅ Instala `ffmpeg` (processamento de áudio)
- ✅ Instala `libsndfile1` (leitura de arquivos de áudio)
- ✅ Instala `portaudio19-dev` (suporte de áudio)

**macOS:**
- ✅ Verifica e instala `ffmpeg` via Homebrew (se disponível)

**Windows:**
- ⚠️ Orienta sobre instalação manual do FFmpeg
- ✅ Fornece links e instruções detalhadas

### Passo 4: Dependências Python
- ✅ Instala todos os pacotes do `requirements.txt`:
  - `pyannote.audio` - Diarização
  - `whisperx` - Transcrição
  - `speechbrain` - Identificação de falantes
  - `torch` - Backend de deep learning
  - `gradio` - Interface web
  - E outros...

⏱️ **Tempo estimado:** 5-15 minutos (depende da conexão)

### Passo 5: Estrutura de Diretórios
- ✅ Cria pasta `output/` (relatórios gerados)
- ✅ Cria pasta `samples/` (amostras de referência)
- ✅ Cria pasta `models/` (modelos baixados)
- ✅ Cria pasta `templates/` (templates HTML)

### Passo 6: Configuração do Hugging Face
- ✅ Solicita o token de acesso (obrigatório)
- ✅ Atualiza automaticamente o `config.yaml`
- ✅ Fornece instruções passo a passo

### Passo 7: Script de Inicialização
- ✅ Cria `iniciar.sh` (Linux/macOS) ou `iniciar.bat` (Windows)
- ✅ Script pronto para rodar a aplicação com um comando

---

## 🎯 Pós-Instalação

### Iniciar a Aplicação

**Linux/macOS:**
```bash
./iniciar.sh
```

**Windows:**
```cmd
iniciar.bat
```

Ou manualmente:

**Linux/macOS:**
```bash
source venv/bin/activate
python -m src.app
```

**Windows:**
```cmd
call venv\Scripts\activate
python -m src.app
```

### Acessar a Interface

Após iniciar, acesse no navegador:
```
http://localhost:7860
```

---

## 🔧 Solução de Problemas

### Erro: "Python não encontrado"

**Solução:**
- Instale Python 3.10 ou superior em https://www.python.org/downloads/
- No Windows, marque a opção **"Add Python to PATH"** durante a instalação

### Erro: "Token de acesso inválido"

**Solução:**
1. Acesse https://huggingface.co/join e crie uma conta
2. Aceite os termos dos modelos:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. Gere um token em https://huggingface.co/settings/tokens
4. Execute o instalador novamente ou edite `config.yaml` manualmente

### Erro: "FFmpeg não encontrado" (Windows)

**Solução:**
1. Baixe FFmpeg em https://www.gyan.dev/ffmpeg/builds/
2. Extraia o arquivo ZIP
3. Adicione a pasta `bin` ao PATH do Windows
4. Reinicie o terminal

### Instalação muito lenta

**Causa:** Download dos modelos de machine learning

**Solução:**
- Tenha paciência (pode levar 10-15 minutos)
- Use uma conexão de internet estável
- Os modelos são baixados apenas na primeira execução

---

## 📝 Instalação Manual (Alternativa)

Se preferir não usar os scripts automáticos, siga o guia completo no arquivo `README.md`.

---

## ✅ Checklist de Verificação

Após a instalação, verifique:

- [ ] Ambiente virtual criado (`venv/` existe)
- [ ] Dependências instaladas (sem mensagens de erro)
- [ ] Diretórios criados (`output/`, `samples/`, `models/`, `templates/`)
- [ ] Token do Hugging Face configurado em `config.yaml`
- [ ] Script de inicialização criado (`iniciar.sh` ou `iniciar.bat`)
- [ ] Aplicação inicia sem erros
- [ ] Interface acessível em http://localhost:7860

---

## 🆘 Suporte

Se encontrar problemas não documentados aqui:

1. Consulte o `README.md` principal
2. Verifique o `MANUAL_USUARIO.md`
3. Revise os logs de erro durante a instalação
4. Certifique-se de ter seguido todos os passos

---

**Última atualização:** Agosto 2024  
**Versão do instalador:** 1.0.0
