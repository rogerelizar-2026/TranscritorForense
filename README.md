# 🏗️ STACK TECNOLÓGICO

Python 3.10+
├── pyannote.audio 3.1.1      # Diarização acústica real
├── whisperx 3.1.1            # Transcrição + alinhamento fonético
├── speechbrain 1.0.0         # Identificação por amostras de voz
├── torch 2.1.0 + CUDA        # Backend GPU (opcional, funciona em CPU)
├── gradio 4.x                # Interface web local
├── jinja2                    # Templates HTML forense
└── pyyaml                    # Configuração

## Requisitos de hardware:
- **Mínimo:** 16 GB RAM, CPU moderna (funciona, mas lento)
- **Recomendado:** NVIDIA GPU com 8+ GB VRAM (RTX 3060 ou superior)

---

# 📁 ESTRUTURA DO REPOSITÓRIO

```
transcritor-forense/
├── .gitignore
├── README.md
├── requirements.txt
├── config.yaml
│
├── src/
│   ├── __init__.py             # Pacote principal
│   ├── diarizer.py             # pyannote.audio wrapper
│   ├── transcriber.py          # whisperx wrapper  
│   ├── speaker_identifier.py   # SpeechBrain + amostras
│   ├── forensic_formatter.py   # Gera MD/TXT/HTML forense
│   ├── speaker_mapper.py       # Mapeia SPEAKER_XX → nomes
│   └── app.py                  # Interface Gradio
│
├── templates/                  # Templates Jinja2 (opcional)
│   ├── forensic_report.html
│   └── forensic_report.md
│
├── samples/                    # Amostras de voz de referência
│   ├── cliente.wav
│   └── empresa.wav
│
├── models/                     # Modelos baixados (gitignored)
│
├── output/                     # Transcrições geradas
│
└── tests/
    ├── test_diarizer.py
    └── test_formatter_standalone.py
```

---

# ⚡ INSTALAÇÃO RÁPIDA

## 1. Clonar repositório
```bash
git clone <repo-url>
cd transcritor-forense
```

## 2. Criar ambiente virtual (recomendado)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

## 3. Instalar dependências
```bash
pip install -r requirements.txt
```

## 4. Obter token Hugging Face (OBRIGATÓRIO para pyannote.audio)

1. Crie conta em https://huggingface.co
2. Aceite os termos dos modelos:
   - https://huggingface.co/pyannote/speaker-diarization-3.1
   - https://huggingface.co/pyannote/segmentation-3.0
3. Gere token em https://huggingface.co/settings/tokens
4. Atualize `config.yaml` com seu token:
```yaml
huggingface_token: "hf_seu_token_aqui"
```

---

# 🚀 USO

## Via Interface Web (Recomendado)

```bash
python -m src.app
```

Acesse http://localhost:7860 no navegador.

### Funcionalidades da interface:
1. **Upload de áudio** - Carregue arquivos WAV, MP3, OGG, FLAC
2. **Amostras de referência** - Carregue amostras de voz para identificação automática
3. **Processamento** - Diarização + Transcrição + Identificação
4. **Mapeamento manual** - Corrija nomes dos falantes se necessário
5. **Gerar relatório** - Exporte em Markdown, TXT ou HTML

## Via Linha de Comando (Programático)

```python
from src import ForensicFormatter, SpeakerMapper

# Inicializa componentes
formatter = ForensicFormatter(output_dir="output")
mapper = SpeakerMapper()

# Mapeia falantes manualmente
mapper.map_speaker("SPEAKER_00", "Cliente", confidence=1.0, method="manual")
mapper.map_speaker("SPEAKER_01", "Atendente", confidence=1.0, method="manual")

# Gera relatório (após obter segmentos de outra fonte)
segments = [
    {"speaker": "SPEAKER_00", "start": 0.0, "end": 5.0, "text": "Olá, bom dia!"},
    {"speaker": "SPEAKER_01", "start": 5.0, "end": 10.0, "text": "Bom dia, como posso ajudar?"}
]

files = formatter.generate_full_report(
    audio_path="audio/negociacao.wav",
    segments=segments,
    speaker_map={"SPEAKER_00": "Cliente", "SPEAKER_01": "Atendente"},
    speaker_mappings=mapper.get_all_mappings(),
    formats=["markdown", "html", "txt"]
)

print(f"Relatórios gerados: {files}")
```

---

# 📋 METODOLOGIA FORENSE

Esta ferramenta foi desenvolvida para produzir documentos com **validade jurídica** em processos de defesa do consumidor. Diferente de soluções baseadas apenas em LLMs, nossa abordagem combina:

## 1. Diarização Acústica Real (pyannote.audio)
- **Não é inferência contextual** - análise espectral baseada em deep learning
- Detecta mudanças de falante por características acústicas do sinal de áudio
- Fornece timestamps precisos de quem fala e quando

## 2. Transcrição com Alinhamento Fonético (whisperx)
- Whisper da OpenAI para transcrição de alta precisão
- Alinhamento word-level por modelos fonéticos
- Timestamps precisos para cada palavra

## 3. Identificação por Amostras de Voz (speechbrain)
- ECAPA-TDNN para extração de embeddings de voz
- Compara segmentos com amostras de referência fornecidas
- Threshold configurável para identificação confiável

## 4. Formatação Forense
- Hash SHA-256 do áudio original em todos os relatórios
- Metadados completos de processamento
- Documentação da metodologia aplicada
- Múltiplos formatos (MD, TXT, HTML)

---

# ⚙️ CONFIGURAÇÃO

Edite `config.yaml`:

```yaml
# Token Hugging Face (obrigatório)
huggingface_token: "hf_seu_token_aqui"

# Modelos
diarization_model: "pyannote/speaker-diarization-3.1"
transcription_model: "large-v2"  # tiny, base, small, medium, large-v1, large-v2, large-v3
embedding_model: "speechbrain/spkrec-ecapa-voxceleb"

# Parâmetros
min_speakers: 2
max_speakers: 5
language: "pt"
speaker_identification_threshold: 0.75

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

---

# 🧪 TESTES

Execute testes unitários:

```bash
# Testes do formatter (não requer dependências externas)
python tests/test_formatter_standalone.py

# Testes completos (requer todas as dependências instaladas)
python -m unittest discover tests
```

---

# 📄 EXEMPLO DE RELATÓRIO

## Markdown
```markdown
# RELATÓRIO DE TRANSCRIÇÃO FORENSE

## METADADOS TÉCNICOS
- **Arquivo de Áudio:** negociacao.wav
- **Hash SHA-256:** `abc123...`
- **Data de Processamento:** 2024-01-15T10:30:00
- **Duração Total:** 05:23.456
- **Falantes Identificados:** 2

## MAPEAMENTO DE FALANTES
| ID Original | Nome Identificado | Método | Confiança |
|-------------|-------------------|--------|-----------|
| SPEAKER_00  | Cliente           | manual | 100%      |
| SPEAKER_01  | Atendente         | auto   | 87%       |

## TRANSCRIÇÃO
**[00:00] Cliente:**
  Olá, gostaria de fazer uma reclamação sobre...

**[00:05] Atendente:**
  Bom dia, senhor. Em que posso ajudar?
```

---

# 🔒 VALIDADE JURÍDICA

Os relatórios gerados incluem:

1. **Hash criptográfico** do áudio original (SHA-256)
2. **Timestamps precisos** com alinhamento fonético
3. **Metadados completos** de processamento
4. **Documentação da metodologia** aplicada
5. **Versão da ferramenta** utilizada

Isso permite:
- Verificação de integridade do áudio original
- Reprodutibilidade do processo
- Auditoria técnica do laudo

---

# ⚠️ LIMITAÇÕES

1. **Qualidade do áudio:** Áudios muito ruidosos ou com baixa qualidade podem ter precisão reduzida
2. **Falantes sobrepostos:** Diálogos simultâneos podem não ser detectados corretamente
3. **Identificação por amostras:** Requer amostras de referência com qualidade similar ao áudio alvo
4. **Idioma:** Modelo otimizado para português brasileiro

---

# 📝 LICENÇA

Verifique o arquivo LICENSE para termos de uso.

---

# 🤝 SUPORTE

Para issues e contribuições, utilize o sistema de issues do repositório.
