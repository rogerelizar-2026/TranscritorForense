🏗️ STACK TECNOLÓGICO
Python 3.10+
├── pyannote.audio 3.1.1      # Diarização
├── whisperx 3.1.1            # Transcrição + alinhamento
├── speechbrain 0.5.16        # Identificação por amostras
├── torch 2.1.0 + CUDA        # Backend GPU
├── gradio 4.x                # Interface web local
├── jinja2                    # Templates HTML forense
└── pyyaml                    # Configuração

Requisitos de hardware:
- Mínimo: 16 GB RAM, CPU moderna (funciona, mas lento)
- Recomendado: NVIDIA GPU com 8+ GB VRAM (RTX 3060 ou superior)

📁 ESTRUTURA DO REPOSITÓRIO
transcritor-forense/
├── .gitignore
├── README.md
├── requirements.txt
├── config.yaml
├── setup.py                    # Script de instalação inicial
│
├── src/
│   ├── __init__.py
│   ├── diarizer.py             # pyannote wrapper
│   ├── transcriber.py          # whisperx wrapper
│   ├── speaker_identifier.py   # SpeechBrain + amostras
│   ├── forensic_formatter.py   # Gera MD/TXT/HTML
│   ├── speaker_mapper.py       # Mapeia SPEAKER_XX → nomes
│   └── app.py                  # Interface Gradio
│
├── templates/
│   ├── forensic_report.html    # Template HTML forense
│   └── forensic_report.md      # Template Markdown
│
├── samples/                    # Amostras de voz de referência
│   ├── rogério.wav
│   ├── anselmo.wav
│   ├── nicolas.wav
│   └── tiago.wav
│
├── models/                     # Modelos baixados (gitignored)
│
├── output/                     # Transcrições geradas
│
└── tests/
    ├── test_diarizer.py
    └── test_formatter.py

💻 CÓDIGO BASE (Pronto para Implementação)
pyannote.audio==3.1.1
whisperx==3.1.1
speechbrain==1.0.0
torch==2.1.0
torchaudio==2.1.0
gradio==4.31.0
jinja2==3.1.3
pyyaml==6.0.1
numpy<2.0.0
soundfile==0.12.1
librosa==0.10.1
