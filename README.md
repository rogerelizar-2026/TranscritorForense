# ⚖️ Transcritor Forense de Áudio

**Ferramenta profissional de transcrição forense para produção de documentos com validade jurídica em processos de defesa do consumidor.**

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Licença](https://img.shields.io/badge/Licença-MIT-green.svg)

---

## 🎯 Propósito

Esta ferramenta foi desenvolvida para **advogados e consultores** que necessitam produzir **laudos técnicos de transcrição de áudio** com precisão forense, especialmente em casos envolvendo:

- ✅ Negociações gravadas entre consumidores e empresas
- ✅ Call centers e atendimento telefônico
- ✅ Reuniões e conversas presenciais gravadas
- ✅ Provas audiovisuais em processos judiciais

### ❗ Por que esta ferramenta é diferente?

Soluções baseadas apenas em LLMs (como ChatGPT) **não fazem análise espectral real** — elas inferem quem fala pelo contexto, não por características acústicas. Isso é **inaceitável para documentos jurídicos**.

Nossa solução combina:

| Componente | Tecnologia | Função |
|------------|------------|--------|
| **Diarização** | pyannote.audio 3.1.1 | Identifica **quem fala e quando** por análise espectral |
| **Transcrição** | whisperx 3.1.1 | Transcreve **o que foi dito** com alinhamento fonético |
| **Identificação** | SpeechBrain 1.0.0 | Reconhece falantes por **amostras de voz de referência** |
| **Formatação** | Jinja2 + Custom | Gera relatórios em **MD/TXT/HTML** com hashes criptográficos |

---

## 🏗️ Stack Tecnológico

```
Python 3.10+
├── pyannote.audio 3.1.1      # Diarização acústica real
├── whisperx 3.1.1            # Transcrição + alinhamento fonético
├── speechbrain 1.0.0         # Identificação por amostras de voz
├── torch 2.1.0 + CUDA        # Backend GPU (opcional, funciona em CPU)
├── gradio 4.x                # Interface web local
├── jinja2                    # Templates HTML forense
└── pyyaml                    # Configuração
```

### Requisitos de Hardware

| Configuração | Especificação | Performance Esperada |
|--------------|---------------|----------------------|
| **Mínimo** | 16 GB RAM, CPU moderna | Funciona, mas lento (~1 minuto de áudio = 5-10 minutos) |
| **Recomendado** | NVIDIA GPU com 8+ GB VRAM (RTX 3060+) | Rápido (~1 minuto de áudio = 30-60 segundos) |
| **Ideal** | NVIDIA GPU com 12+ GB VRAM (RTX 3080/4070+) | Muito rápido (~1 minuto de áudio = 15-30 segundos) |

---

## 📁 Estrutura do Repositório

```
transcritor-forense/
├── README.md                   # Este arquivo
├── MANUAL_USUARIO.md           # Manual passo a passo
├── requirements.txt            # Dependências Python
├── config.yaml                 # Configurações
│
├── src/
│   ├── __init__.py             # Pacote principal
│   ├── diarizer.py             # Diarização com pyannote.audio
│   ├── transcriber.py          # Transcrição com whisperx
│   ├── speaker_identifier.py   # Identificação com SpeechBrain
│   ├── speaker_mapper.py       # Mapeamento SPEAKER_XX → nomes
│   ├── forensic_formatter.py   # Relatórios MD/TXT/HTML
│   └── app.py                  # Interface Gradio
│
├── templates/                  # Templates Jinja2
│   ├── forensic_report.html
│   └── forensic_report.md
│
├── samples/                    # Amostras de voz de referência
│   ├── cliente.wav
│   └── empresa.wav
│
├── models/                     # Modelos baixados (gitignored)
├── output/                     # Transcrições geradas
│
└── tests/                      # Testes unitários
    ├── test_diarizer.py
    └── test_formatter_standalone.py
```

---

## ⚡ Instalação Passo a Passo

### Pré-requisitos

1. **Python 3.10 ou superior** instalado
   ```bash
   python --version  # Deve mostrar Python 3.10.x ou superior
   ```

2. **Git** instalado (para clonar o repositório)

3. **Conta no Hugging Face** (gratuita) - obrigatória para usar pyannote.audio

---

### Passo 1: Clonar o Repositório

```bash
cd ~/projetos  # ou qualquer diretório de sua preferência
git clone <URL_DO_REPOSITORIO> transcritor-forense
cd transcritor-forense
```

---

### Passo 2: Criar Ambiente Virtual (Recomendado)

**Linux/macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

Você verá `(venv)` no início do prompt, indicando que o ambiente virtual está ativo.

---

### Passo 3: Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏱️ **Tempo estimado:** 5-15 minutos (dependendo da conexão)

> **Nota:** Se tiver GPU NVIDIA, certifique-se de ter os drivers CUDA instalados. O pacote detectará automaticamente e usará GPU se disponível.

---

### Passo 4: Obter Token do Hugging Face (OBRIGATÓRIO)

Os modelos `pyannote.audio` exigem autenticação. Siga estes passos:

#### 4.1. Crie uma conta no Hugging Face

1. Acesse https://huggingface.co
2. Clique em **"Sign Up"** (canto superior direito)
3. Preencha email, senha e username
4. Confirme seu email

#### 4.2. Aceite os Termos dos Modelos

Você precisa aceitar os termos de uso de DOIS modelos:

1. **Speaker Diarization:**
   - Acesse: https://huggingface.co/pyannote/speaker-diarization-3.1
   - Role até encontrar a seção "Access token"
   - Clique em **"Agree and access repository"**

2. **Segmentation:**
   - Acesse: https://huggingface.co/pyannote/segmentation-3.0
   - Clique em **"Agree and access repository"**

#### 4.3. Gere seu Token de Acesso

1. Acesse: https://huggingface.co/settings/tokens
2. Clique em **"New token"**
3. Dê um nome (ex: `transcritor-forense`)
4. Selecione o tipo: **"Read"** (leitura é suficiente)
5. Clique em **"Generate token"**
6. **Copie o token** (começa com `hf_`) - você só consegue vê-lo uma vez!

#### 4.4. Configure o Token no Projeto

Edite o arquivo `config.yaml`:

```bash
nano config.yaml  # ou use seu editor preferido
```

Substitua a linha:
```yaml
huggingface_token: "hf_seu_token_aqui"
```

Pelo seu token real:
```yaml
huggingface_token: "hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
```

Salve o arquivo (no nano: `Ctrl+O`, `Enter`, `Ctrl+X`).

---

### Passo 5: Verificar Instalação

Execute os testes unitários para verificar se tudo está funcionando:

```bash
python tests/test_formatter_standalone.py
```

Se ver `OK` no final, a instalação básica está correta.

---

## 🚀 Como Usar - Guia Passo a Passo

### Método 1: Interface Web (Recomendado para Iniciantes)

#### Passo 1: Iniciar a Aplicação

Com o ambiente virtual ativado:

```bash
python -m src.app
```

Você verá algo como:
```
Running on local URL: http://localhost:7860
```

#### Passo 2: Acessar no Navegador

Abra seu navegador e acesse: **http://localhost:7860**

#### Passo 3: Carregar o Áudio

1. Na seção **"Upload de Áudio"**, clique em **"Browse files"**
2. Selecione seu arquivo de áudio (WAV, MP3, OGG, FLAC)
3. Aguarde o upload completar

> **Dica:** Arquivos WAV sem compressão oferecem melhor qualidade, mas são maiores. MP3 é aceitável para a maioria dos casos.

#### Passo 4: (Opcional) Carregar Amostras de Referência

Para identificação automática dos falantes:

1. Na seção **"Amostras de Referência"**, carregue arquivos de áudio curtos (5-30 segundos) de cada falante conhecido
2. Exemplo: 
   - `cliente.wav` → amostra da voz do cliente
   - `empresa.wav` → amostra da voz do atendente da empresa

> **Importante:** As amostras devem ser da MESMA pessoa que aparece na gravação principal. Qualidade similar ajuda na precisão.

#### Passo 5: Configurar Parâmetros

Ajuste conforme necessário:

| Parâmetro | Valor Recomendado | Descrição |
|-----------|-------------------|-----------|
| Número mínimo de falantes | 2 | Geralmente cliente + atendente |
| Número máximo de falantes | 5 | Ajuste se houver mais participantes |
| Idioma | pt | Português brasileiro |
| Threshold de identificação | 0.75 | Confiança mínima para auto-identificação |

#### Passo 6: Processar

Clique em **"🔄 Processar Áudio"** e aguarde.

⏱️ **Tempo de processamento:**
- Com GPU: ~30-60 segundos por minuto de áudio
- Sem GPU: ~5-10 minutos por minuto de áudio

#### Passo 7: Revisar e Mapear Falantes

Após o processamento, você verá:

1. **Tabela de Falantes Detectados** - lista de `SPEAKER_00`, `SPEAKER_01`, etc.
2. **Campos para Mapeamento** - digite os nomes reais (ex: "Cliente", "Atendente")
3. **Prévia da Transcrição** - texto transcrito com timestamps

Edite os nomes conforme necessário.

#### Passo 8: Gerar Relatório

Clique em **"📄 Gerar Relatório Forense"**.

O relatório será gerado em múltiplos formatos:
- 📝 **Markdown (.md)** - para documentação técnica
- 📄 **Texto (.txt)** - para anexos simples
- 🌐 **HTML (.html)** - para visualização formatada

Os arquivos serão salvos na pasta `output/`.

---

### Método 2: Linha de Comando (Para Usuários Avançados)

Crie um script Python:

```python
# processar_audio.py
from src.diarizer import Diarizer
from src.transcriber import Transcriber
from src.speaker_identifier import SpeakerIdentifier
from src.speaker_mapper import SpeakerMapper
from src.forensic_formatter import ForensicFormatter
import yaml

# Carregar configuração
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Inicializar componentes
diarizer = Diarizer(config)
transcriber = Transcriber(config)
identifier = SpeakerIdentifier(config)
mapper = SpeakerMapper()
formatter = ForensicFormatter(output_dir='output')

# Caminhos
audio_path = 'samples/negociacao.wav'
amostras = {
    'cliente': 'samples/cliente_ref.wav',
    'empresa': 'samples/empresa_ref.wav'
}

print("1. Diarizando áudio...")
segmentos = diarizer.diarize(audio_path)
print(f"   {len(segmentos)} segmentos encontrados")

print("2. Transcrevendo...")
segmentos = transcriber.transcribe_with_alignment(audio_path, segmentos)

print("3. Identificando falantes por amostras...")
for nome, caminho in amostras.items():
    identifier.add_reference_sample(nome, caminho)

segmentos_com_id = identifier.identify_from_samples(segmentos, threshold=0.75)

print("4. Mapeando falantes restantes manualmente...")
for seg in segmentos_com_id:
    if seg['speaker'].startswith('SPEAKER_'):
        # Mapeamento manual baseado na análise do conteúdo
        if "quero cancelar" in seg['text'].lower():
            mapper.map_speaker(seg['speaker'], 'Cliente', confidence=1.0, method='manual')
        else:
            mapper.map_speaker(seg['speaker'], 'Atendente', confidence=1.0, method='manual')

print("5. Gerando relatório forense...")
files = formatter.generate_full_report(
    audio_path=audio_path,
    segments=segmentos_com_id,
    speaker_map=mapper.get_speaker_map(),
    speaker_mappings=mapper.get_all_mappings(),
    formats=['markdown', 'html', 'txt']
)

print(f"\n✅ Relatórios gerados:")
for f in files:
    print(f"   - {f}")
```

Execute:
```bash
python processar_audio.py
```

---

## 📋 Metodologia Forense

Esta ferramenta segue princípios de **perícia técnica digital** para garantir validade jurídica:

### 1. Diarização Acústica Real (pyannote.audio)

- ❌ **NÃO** é inferência contextual (como LLMs fazem)
- ✅ Análise espectral baseada em deep learning
- ✅ Detecta mudanças de falante por características acústicas do sinal
- ✅ Timestamps precisos de início e fim de cada turno de fala

### 2. Transcrição com Alinhamento Fonético (whisperx)

- ✅ Whisper da OpenAI para alta precisão em português
- ✅ Alinhamento word-level por modelos fonéticos
- ✅ Cada palavra tem timestamp preciso de início e fim
- ✅ Detecta incertezas e marca trechos pouco claros

### 3. Identificação por Amostras de Voz (SpeechBrain)

- ✅ ECAPA-TDNN para extração de embeddings de voz
- ✅ Compara segmentos com amostras de referência
- ✅ Threshold configurável (recomendado: 0.75)
- ✅ Score de confiança documentado no relatório

### 4. Formatação Forense

- ✅ Hash SHA-256 do áudio original em todos os relatórios
- ✅ Metadados completos de processamento
- ✅ Documentação da metodologia aplicada
- ✅ Versão da ferramenta utilizada
- ✅ Múltiplos formatos de exportação

---

## 📄 Exemplo de Relatório

### Markdown (trecho)

```markdown
# RELATÓRIO DE TRANSCRIÇÃO FORENSE

## METADADOS TÉCNICOS
- **Arquivo de Áudio:** negociacao.wav
- **Hash SHA-256:** abc123def456...
- **Data de Processamento:** 2024-01-15T10:30:00
- **Duração Total:** 05:23.456
- **Falantes Identificados:** 2
- **Ferramenta:** Transcritor Forense v1.0.0

## MAPEAMENTO DE FALANTES
| ID Original | Nome Identificado | Método  | Confiança |
|-------------|-------------------|---------|-----------|
| SPEAKER_00  | Cliente           | manual  | 100%      |
| SPEAKER_01  | Atendente         | auto    | 87%       |

## TRANSCRIÇÃO

**[00:00.000] Cliente:**
  Olá, bom dia! Gostaria de fazer uma reclamação sobre 
  uma cobrança indevida na minha fatura.

**[00:05.230] Atendente:**
  Bom dia, senhor. Em que posso ajudar? O senhor poderia 
  me informar seu CPF para consulta?

**[00:10.450] Cliente:**
  Sim, é 123.456.789-00.
```

---

## 🔒 Validade Jurídica

Os relatórios gerados incluem elementos que garantem **autenticidade e integridade**:

| Elemento | Finalidade |
|----------|------------|
| **Hash SHA-256** | Permite verificar que o áudio não foi alterado |
| **Timestamps precisos** | Localiza exatamente onde cada fala ocorre |
| **Metadados de processamento** | Documenta quando e como foi gerado |
| **Versão da ferramenta** | Permite reprodutibilidade |
| **Metodologia documentada** | Explica tecnicamente o processo |

### Como usar em processos judiciais:

1. **Anexe o relatório** em formato PDF (converta do HTML)
2. **Disponibilize o áudio original** para conferência do hash
3. **Inclua este README** como anexo técnico explicativo
4. **Ofereça-se para periciar** - a ferramenta é reproduzível

---

## ⚙️ Configuração Avançada

Edite `config.yaml` para personalizar:

```yaml
# Token Hugging Face (obrigatório)
huggingface_token: "hf_seu_token_aqui"

# Modelos
diarization_model: "pyannote/speaker-diarization-3.1"
transcription_model: "large-v2"  # tiny, base, small, medium, large-v1/v2/v3
embedding_model: "speechbrain/spkrec-ecapa-voxceleb"

# Parâmetros de diarização
min_speakers: 2
max_speakers: 5

# Idioma
language: "pt"

# Identificação de falantes
speaker_identification_threshold: 0.75  # 0.0 a 1.0

# Output
output_dir: "output"
formats:
  - markdown
  - html
  - txt

# Metadados forenses
include_metadata: true
include_hashes: true
include_timestamps: true
```

### Escolha do Modelo de Transcrição

| Modelo | Tamanho | Velocidade | Precisão | Uso Recomendado |
|--------|---------|------------|----------|-----------------|
| `tiny` | ~39 MB | Muito rápida | Baixa | Testes rápidos |
| `base` | ~74 MB | Rápida | Média | Áudios curtos e claros |
| `small` | ~244 MB | Moderada | Boa | Uso geral |
| `medium` | ~769 MB | Lenta | Muito boa | Áudios importantes |
| `large-v2` | ~1.5 GB | Muito lenta | Excelente | **Recomendado para perícia** |

---

## 🧪 Testes

Execute os testes unitários:

```bash
# Testes do formatter (não requer dependências externas)
python tests/test_formatter_standalone.py

# Testes completos (requer todas as dependências)
python -m unittest discover tests
```

---

## ⚠️ Limitações e Boas Práticas

### Limitações Técnicas

| Limitação | Impacto | Mitigação |
|-----------|---------|-----------|
| Áudio muito ruidoso | Precisão reduzida | Use filtro de ruído antes |
| Falantes sobrepostos | Pode não detectar | Peça para revisar manualmente |
| Amostras de baixa qualidade | Identificação falha | Use amostras de 10-30s em qualidade similar |
| Sotaques muito fortes | Erros de transcrição | Revise trechos críticos manualmente |

### Boas Práticas para Advogados

1. ✅ **Sempre revise** a transcrição gerada - nenhuma ferramenta é 100% precisa
2. ✅ **Mantenha o áudio original** intacto - o hash deve bater
3. ✅ **Documente o processo** - salve logs e versões usadas
4. ✅ **Use amostras de referência** sempre que possível
5. ✅ **Teste antes do caso real** - familiarize-se com a ferramenta

---

## 🆘 Solução de Problemas

### Erro: "Token de acesso inválido"

**Causa:** Token do Hugging Face incorreto ou não configurado

**Solução:**
1. Verifique se aceitou os termos em ambos os links (seção 4.2)
2. Gere um novo token em https://huggingface.co/settings/tokens
3. Atualize `config.yaml` com o novo token
4. Reinicie a aplicação

---

### Erro: "CUDA out of memory"

**Causa:** GPU sem memória suficiente para o modelo

**Solução:**
1. Use um modelo menor (`small` ou `medium` em vez de `large-v2`)
2. Feche outros programas usando GPU
3. Force uso de CPU edite `config.yaml`:
   ```yaml
   device: "cpu"
   ```

---

### Erro: "ModuleNotFoundError"

**Causa:** Dependências não instaladas corretamente

**Solução:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

### Processamento muito lento

**Causa:** Rodando em CPU sem GPU

**Solução:**
- Instale drivers CUDA se tiver GPU NVIDIA
- Use modelos menores (`small` em vez de `large`)
- Processe áudios longos em partes

---

## 📞 Suporte

Para issues, dúvidas ou contribuições:

1. Abra uma issue no repositório GitHub
2. Inclua:
   - Versão do Python
   - Sistema operacional
   - Mensagem de erro completa
   - Trecho do áudio (se possível)

---

## 📝 Licença

Verifique o arquivo `LICENSE` para termos de uso.

---

## 📚 Referências Técnicas

- **pyannote.audio:** https://github.com/pyannote/pyannote-audio
- **whisperx:** https://github.com/m-bain/whisperx
- **SpeechBrain:** https://speechbrain.github.io/
- **Hugging Face:** https://huggingface.co/docs

---

**Desenvolvido para profissionais do direito que necessitam de precisão técnica em provas audiovisuais.**
