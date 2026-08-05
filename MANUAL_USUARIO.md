# 📘 Manual do Usuário - Transcritor Forense de Áudio

**Guia completo passo a passo para instalação e uso da ferramenta de diarização de áudio.**

---

## 📋 Índice

1. [Visão Geral](#1-visão-geral)
2. [Pré-requisitos](#2-pré-requisitos)
3. [Instalação Completa](#3-instalação-completa)
4. [Configuração do Hugging Face](#4-configuração-do-hugging-face-obrigatório)
5. [Primeiro Uso - Diarizar um Áudio](#5-primeiro-uso---diarizar-um-áudio)
6. [Interpretando os Resultados](#6-interpretando-os-resultados)
7. [Gerando Relatórios Forenses](#7-gerando-relatórios-forenses)
8. [Perguntas Frequentes](#8-perguntas-frequentes)

---

## 1. Visão Geral

### O que esta ferramenta faz?

Esta ferramenta transforma **áudios de negociações gravadas** em **documentos textuais formatados** com validade jurídica, identificando:

- ✅ **QUEM falou** (diarização por análise espectral)
- ✅ **QUANDO falou** (timestamps precisos)
- ✅ **O QUE foi dito** (transcrição automática)

### Para quem é esta ferramenta?

- **Advogados** que atuam em defesa do consumidor
- **Consultores jurídicos** que analisam gravações
- **Peritos técnicos** que produzem laudos de áudio
- **Escritórios de advocacia** que necessitam transcrever negociações

### Fluxo de Trabalho

```
Áudio Original → Diarização → Transcrição → Identificação → Relatório Forense
     ↓              ↓             ↓              ↓              ↓
  (WAV/MP3)   (quem fala)    (o que diz)   (nomes reais)   (MD/TXT/HTML)
```

---

## 2. Pré-requisitos

Antes de começar, verifique se você tem:

### 2.1. Sistema Operacional

✅ Funciona em:
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, Debian 11+)

### 2.2. Python 3.10 ou Superior

**Como verificar:**

Abra o terminal (ou Prompt de Comando no Windows) e digite:

```bash
python --version
```

**Se aparecer algo como `Python 3.9.x` ou inferior:**

Você precisa atualizar o Python:

- **Windows:** Baixe em https://www.python.org/downloads/windows/
- **macOS:** `brew install python@3.10` (se tiver Homebrew)
- **Linux:** `sudo apt update && sudo apt install python3.10`

### 2.3. Espaço em Disco

Você precisará de aproximadamente:

- **5 GB** para as dependências
- **2-10 GB** para os modelos (baixados automaticamente)
- **Espaço adicional** para áudios e relatórios

**Total recomendado:** 20 GB livres

### 2.4. Conexão com Internet

Necessária apenas para:
- Instalação inicial (baixar dependências)
- Primeiro uso (baixar modelos do Hugging Face)

Depois de instalado, **funciona offline**.

### 2.5. GPU (Opcional mas Recomendado)

Se você tem uma placa de vídeo NVIDIA:

- **Vantagem:** Processamento 10-20x mais rápido
- **Requisito:** Drivers CUDA instalados
- **Verificar:** `nvidia-smi` no terminal

**Não tem GPU?** Funciona normalmente na CPU, só será mais lento.

---

## 3. Instalação Completa

Siga estes passos **na ordem exata**:

### Passo 3.1: Baixar o Projeto

Abra o terminal e navegue até onde quer salvar o projeto:

```bash
cd ~/Documentos  # ou qualquer pasta de sua preferência
```

Clone o repositório (substitua pela URL real):

```bash
git clone <URL_DO_REPOSITORIO> transcritor-forense
cd transcritor-forense
```

**Se não tem Git:** Baixe o ZIP do repositório e extraia na pasta desejada.

### Passo 3.2: Criar Ambiente Virtual

Um ambiente virtual isola as dependências deste projeto das outras instalações Python.

**No Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**No Linux/macOS:**

```bash
python -m venv venv
source venv/bin/activate
```

**Como saber se funcionou?**

Você verá `(venv)` no início da linha do terminal:

```
(venv) C:\Users\Voce\Documentos\transcritor-forense>
```

### Passo 3.3: Instalar Dependências

Com o ambiente virtual ativado, execute:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**O que está acontecendo?**

O pip está baixando e instalando:
- pyannote.audio (diarização)
- whisperx (transcrição)
- speechbrain (identificação de voz)
- torch (base de machine learning)
- gradio (interface web)
- E outras dependências...

⏱️ **Tempo estimado:** 5-15 minutos

**Dica:** Se aparecer algum erro, tente:

```bash
pip install -r requirements.txt --no-cache-dir
```

### Passo 3.4: Verificar Instalação

Execute um teste simples:

```bash
python tests/test_formatter_standalone.py
```

Se aparecer `OK` no final, a instalação básica está correta.

---

## 4. Configuração do Hugging Face (OBRIGATÓRIO)

Os modelos de diarização exigem autenticação. Siga **exatamente** estes passos:

### Passo 4.1: Criar Conta no Hugging Face

1. Acesse https://huggingface.co
2. Clique em **"Sign Up"** (canto superior direito)
3. Preencha:
   - Email válido
   - Senha segura
   - Username (nome de usuário)
4. Clique em **"Create account"**
5. Verifique seu email (chegará uma mensagem de confirmação)

### Passo 4.2: Aceitar Termos dos Modelos

**IMPORTANTE:** Você precisa fazer isso para DOIS modelos.

#### Modelo 1: Speaker Diarization

1. Acesse: https://huggingface.co/pyannote/speaker-diarization-3.1
2. Faça login se necessário
3. Role a página até encontrar um botão verde
4. Clique em **"Agree and access repository"**

#### Modelo 2: Segmentation

1. Acesse: https://huggingface.co/pyannote/segmentation-3.0
2. Clique em **"Agree and access repository"**

### Passo 4.3: Gerar Token de Acesso

1. Acesse: https://huggingface.co/settings/tokens
2. Clique no botão **"New token"**
3. Preencha:
   - **Name:** `transcritor-forense` (ou qualquer nome)
   - **Type:** Selecione **"Read"** (leitura é suficiente)
4. Clique em **"Generate token"**
5. **COPIE O TOKEN** imediatamente

⚠️ **ATENÇÃO:** O token aparece apenas UMA VEZ. Se perder, terá que gerar outro.

O token se parece com isto:
```
hf_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789
```

### Passo 4.4: Configurar Token no Projeto

1. Abra o arquivo `config.yaml` em um editor de texto:

   **Windows (Bloco de Notas):**
   ```bash
   notepad config.yaml
   ```

   **Linux/macOS (nano):**
   ```bash
   nano config.yaml
   ```

2. Localize a linha:
   ```yaml
   huggingface_token: "hf_seu_token_aqui"
   ```

3. Substitua pelo SEU token:
   ```yaml
   huggingface_token: "hf_aBcDeFgHiJkLmNoPqRsTuVwXyZ123456789"
   ```

4. Salve o arquivo:
   - **Notepad:** Arquivo → Salvar (ou Ctrl+S)
   - **nano:** Ctrl+O, Enter, Ctrl+X

### Passo 4.5: Testar Configuração

Inicie a aplicação para testar:

```bash
python -m src.app
```

Se aparecer:
```
Running on local URL: http://localhost:7860
```

✅ **Sucesso!** A configuração está correta.

Pressione `Ctrl+C` para parar a aplicação.

---

## 5. Primeiro Uso - Diarizar um Áudio

Agora vamos processar seu primeiro áudio passo a passo.

### Passo 5.1: Preparar o Áudio

**Formatos suportados:**
- WAV (recomendado - melhor qualidade)
- MP3 (aceitável)
- OGG, FLAC, M4A (também funcionam)

**Dicas para melhor qualidade:**

| Fator | Ideal | Evitar |
|-------|-------|--------|
| Formato | WAV 16kHz | MP3 128kbps ou menos |
| Ruído | Mínimo | Música de fundo, estática |
| Duração | Até 30 min | Áudios muito longos (>1h) |
| Falantes | 2-5 pessoas | Muitas vozes simultâneas |

**Coloque seu áudio na pasta:**

```
transcritor-forense/
└── samples/
    └── meu_audio.wav  ← coloque aqui
```

### Passo 5.2: Iniciar a Aplicação

No terminal, com o ambiente virtual ativado:

```bash
python -m src.app
```

Aguarde alguns segundos até aparecer:

```
╭────────────────────────────────────────────────────╮
│  Running on local URL: http://localhost:7860       │
│                                                    │
│  To create a public link, set `share=True`         │
╰────────────────────────────────────────────────────╯
```

### Passo 5.3: Acessar Interface Web

1. Abra seu navegador (Chrome, Firefox, Edge)
2. Digite na barra de endereços: **http://localhost:7860**
3. A interface da aplicação carregará

### Passo 5.4: Carregar o Áudio

Na interface web:

1. Localize a seção **"📁 Upload de Áudio"**
2. Clique em **"Browse files"** ou **"Upload"**
3. Navegue até a pasta `samples/`
4. Selecione seu arquivo de áudio (ex: `meu_audio.wav`)
5. Aguarde o upload completar (barra de progresso)

### Passo 5.5: (Opcional) Carregar Amostras de Referência

Se você tem gravações conhecidas de cada falante:

**Exemplo:** 
- Uma gravação clara da voz do cliente
- Uma gravação clara da voz do atendente

1. Na seção **"🎤 Amostras de Referência"**
2. Clique em **"Adicionar Amostra"**
3. Para cada amostra:
   - **Nome:** Digite o nome (ex: "Cliente", "Atendente")
   - **Arquivo:** Carregue o áudio de referência (5-30 segundos)
4. Repita para cada falante conhecido

> **Nota:** Este passo é opcional. Se não tiver amostras, poderá identificar os falantes manualmente depois.

### Passo 5.6: Configurar Parâmetros

Na seção **"⚙️ Configurações"**, ajuste:

| Campo | Valor Sugerido | Explicação |
|-------|----------------|------------|
| **Mínimo de falantes** | `2` | Cliente + Atendente |
| **Máximo de falantes** | `5` | Aumente se houver mais pessoas |
| **Idioma** | `pt` | Português brasileiro |
| **Threshold identificação** | `0.75` | Confiança mínima (0.0 a 1.0) |

**Quando ajustar?**

- Se souber que são apenas 2 pessoas: coloque `min=2, max=2`
- Se houver música ou ruído: aumente o threshold para `0.85`
- Se os falantes têm sotaques fortes: use threshold menor `0.65`

### Passo 5.7: Processar o Áudio

1. Clique no botão **"🔄 Processar Áudio"**
2. Aguarde o processamento

**Barra de progresso mostrará:**

```
[1/4] Diarizando áudio...
[2/4] Transcrevendo...
[3/4] Identificando falantes...
[4/4] Finalizando...
```

⏱️ **Tempo estimado:**

| Hardware | 1 minuto de áudio | 10 minutos de áudio |
|----------|-------------------|---------------------|
| GPU RTX 3060 | ~30 segundos | ~5 minutos |
| GPU GTX 1060 | ~1 minuto | ~10 minutos |
| CPU (sem GPU) | ~5 minutos | ~50 minutos |

### Passo 5.8: Revisar Resultados

Após o processamento, você verá:

#### Tabela de Falantes Detectados

```
┌─────────────┬──────────────────┬────────────┐
│ ID Original │ Nome Proposto    │ Confiança  │
├─────────────┼──────────────────┼────────────┤
│ SPEAKER_00  │ [editar...]      │ --         │
│ SPEAKER_01  │ [editar...]      │ 87%        │
└─────────────┴──────────────────┴────────────┘
```

**O que fazer:**

1. Nos campos `[editar...]`, digite os nomes reais:
   - `SPEAKER_00` → `Cliente`
   - `SPEAKER_01` → `Atendente Empresa XYZ`

2. Se a identificação automática estiver errada, corrija manualmente

#### Prévia da Transcrição

Você verá algo como:

```
[00:00.000] SPEAKER_00:
  Olá, bom dia! Gostaria de falar sobre minha fatura.

[00:05.230] SPEAKER_01:
  Bom dia! Em que posso ajudar?

[00:08.450] SPEAKER_00:
  Houve uma cobrança indevida no valor de R$ 150,00.
```

**Revise e corrija se necessário:**
- Erros de transcrição são possíveis em áudios ruins
- Nomes próprios e termos técnicos podem precisar de ajuste
- Trechos com ruído podem estar marcados como `[inaudível]`

---

## 6. Interpretando os Resultados

Entenda o que cada informação significa:

### 6.1. Timestamps

Formato: `[MM:SS.mmm]`

Exemplos:
- `[00:00.000]` = Início do áudio
- `[01:30.500]` = 1 minuto, 30 segundos e 500 milissegundos
- `[15:00.000]` = 15 minutos exatos

**Precisão:** Os timestamps são precisos até ~20ms (alinhamento fonético).

### 6.2. IDs de Falante

- `SPEAKER_00`, `SPEAKER_01`, etc. são identificadores temporários
- A numeração é arbitrária - `SPEAKER_00` não é necessariamente "o primeiro a falar"
- Após mapeamento, use os nomes reais nos relatórios

### 6.3. Scores de Confiança

| Valor | Interpretação | Ação Recomendada |
|-------|---------------|------------------|
| 0.90+ | Muito alta | Pode confiar automaticamente |
| 0.75-0.90 | Alta | Confiável, mas revise |
| 0.60-0.75 | Média | Revise manualmente |
| <0.60 | Baixa | Ignore e identifique manualmente |

### 6.4. Marcas Especiais na Transcrição

- `[inaudível]` - Trecho não foi possível entender
- `[música]` - Detecção de música de fundo
- `[risos]` - Detecção de risadas
- `[pausa longa]` - Silêncio prolongado (>3 segundos)
- `<palavra>` - Palavra com baixa confiança

---

## 7. Gerando Relatórios Forenses

### Passo 7.1: Clicar em Gerar Relatório

Após revisar e mapear todos os falantes:

1. Clique em **"📄 Gerar Relatório Forense"**
2. Selecione os formatos desejados:
   - ☑️ Markdown (.md)
   - ☑️ Texto (.txt)
   - ☑️ HTML (.html)

### Passo 7.2: Aguardar Geração

O sistema irá:

1. Calcular hash SHA-256 do áudio original
2. Compilar metadados de processamento
3. Formatar transcrição nos formatos selecionados
4. Salvar arquivos na pasta `output/`

### Passo 7.3: Localizar Arquivos Gerados

Os arquivos serão salvos em:

```
transcritor-forense/
└── output/
    ├── meu_audio_transcription.md
    ├── meu_audio_transcription.txt
    └── meu_audio_transcription.html
```

### Passo 7.4: Usar em Processos Judiciais

#### Para anexar em processo eletrônico:

1. Converta o HTML para PDF:
   - Abra o arquivo `.html` no navegador
   - Imprima (Ctrl+P)
   - Selecione "Salvar como PDF"
   - Salve como `laudo_transcricao.pdf`

2. Anexe no processo:
   - PDF do relatório
   - Áudio original (para conferência do hash)
   - Este manual (como anexo técnico)

#### Para validar integridade:

Qualquer pessoa pode verificar que o áudio não foi alterado:

```bash
# No terminal, na pasta do áudio
sha256sum negociacao.wav

# Compare com o hash no relatório
# Devem ser IDÊNTICOS
```

---

## 8. Perguntas Frequentes

### ❓ Quanto tempo leva para processar?

Depende do hardware e duração do áudio:

| Duração | GPU (RTX 3060) | CPU (i7) |
|---------|----------------|----------|
| 1 minuto | 30-60 seg | 5-10 min |
| 10 minutos | 5-10 min | 50-100 min |
| 30 minutos | 15-30 min | 150-300 min |

**Dica:** Para áudios longos, considere dividir em partes.

---

### ❓ A transcrição ficou com erros. O que fazer?

**Causas possíveis:**

1. **Áudio com ruído:** Use filtro de ruído antes (Audacity, Adobe Audition)
2. **Qualidade baixa:** MP3 128kbps ou inferior perde informação
3. **Sotaque forte:** Revise manualmente trechos problemáticos
4. **Termos técnicos:** Adicione ao dicionário ou corrija pós-processamento

**Solução:** Sempre revise a transcrição antes de usar juridicamente.

---

### ❓ Não tenho amostras de voz. Posso usar mesmo assim?

**Sim!** As amostras são opcionais.

Sem amostras:
- A diarização ainda identifica QUANTOS falantes existem
- Você mapeia manualmente baseado no conteúdo
- Exemplo: quem fala "quero cancelar" provavelmente é o cliente

---

### ❓ Como divido um áudio longo?

Use o **Audacity** (gratuito):

1. Abra o áudio no Audacity
2. Selecione o trecho desejado
3. Arquivo → Exportar → Exportar seleção
4. Salve como `parte1.wav`, `parte2.wav`, etc.
5. Processe cada parte separadamente

---

### ❓ Posso usar em lotes (vários áudios)?

Atualmente a interface web processa **um áudio por vez**.

Para processamento em lote, use o modo programático (veja seção "Método 2" no README.md).

---

### ❓ O token do Hugging Face expira?

**Não**, tokens do tipo "Read" não expiram.

Mas você pode:
- Revogar tokens em https://huggingface.co/settings/tokens
- Gerar novos tokens a qualquer momento

---

### ❓ Funciona sem internet?

**Após a instalação inicial, SIM.**

Uma vez baixados os modelos (primeira execução), a ferramenta funciona 100% offline.

---

### ❓ Onde ficam os modelos baixados?

Por padrão em:

- **Linux/macOS:** `~/.cache/huggingface/hub/`
- **Windows:** `C:\Users\<Voce>\.cache\huggingface\hub\`

São aproximadamente 5-10 GB de modelos.

---

### ❓ Posso compartilhar os relatórios?

**Sim**, mas:

1. Mantenha o hash SHA-256 visível (integridade)
2. Inclua metadados de processamento
3. Informe a versão da ferramenta usada

---

## 🆘 Preciso de Ajuda!

### Erro Comum: "Token inválido"

**Sintoma:** Mensagem de erro mencionando "401 Unauthorized" ou "token invalid"

**Solução:**

1. Verifique se aceitou os termos em AMBOS os links:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0

2. Gere um NOVO token em https://huggingface.co/settings/tokens

3. Atualize o `config.yaml` com o novo token

4. Reinicie a aplicação

---

### Erro Comum: "CUDA out of memory"

**Sintoma:** Erro durante processamento mencionando "OOM" ou "out of memory"

**Solução:**

1. Use modelo menor no `config.yaml`:
   ```yaml
   transcription_model: "small"  # em vez de "large-v2"
   ```

2. Feche outros programas usando GPU

3. Se não tiver GPU, force uso de CPU:
   ```yaml
   device: "cpu"
   ```

---

### Erro Comum: "ModuleNotFoundError"

**Sintoma:** `ModuleNotFoundError: No module named 'pyannote'`

**Solução:**

1. Verifique se o ambiente virtual está ativo (deve ter `(venv)` no prompt)

2. Reinstale as dependências:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

---

## 📞 Contato e Suporte

Se nenhum destes passos resolver seu problema:

1. **Verifique os logs** - A aplicação mostra mensagens de erro detalhadas
2. **Consulte o README.md** - Informações técnicas adicionais
3. **Abra uma issue** - No repositório GitHub do projeto

---

**Última atualização:** Janeiro 2024  
**Versão do manual:** 1.0.0

---

**Desenvolvido para profissionais do direito que necessitam de precisão técnica em provas audiovisuais.**
