# Transcritor de Áudio Simplificado

Versão simplificada e eficiente do Transcritor Forense de Áudio, focada em:
- ✅ Menos erros
- ✅ Mais simplicidade
- ✅ Fácil de usar
- ✅ Funcionalidades essenciais mantidas

## Instalação Rápida

```bash
# Instale as dependências mínimas
pip install torch torchaudio whisperx pyannote.audio speechbrain huggingface_hub

# Ou use o requirements.txt otimizado
pip install -r requirements_simples.txt
```

## Configuração

Defina seu token do Hugging Face (obrigatório para pyannote.audio):

```bash
export HUGGINGFACE_TOKEN="seu_token_aqui"
```

No Windows (PowerShell):
```powershell
$env:HUGGINGFACE_TOKEN="seu_token_aqui"
```

## Uso Básico

### Via Linha de Comando

```bash
# Transcrição simples
python src/transcriber_simples.py audio.mp3

# Com parâmetros personalizados
python src/transcriber_simples.py audio.mp3 --min-speakers 2 --max-speakers 4

# Com amostras de referência para identificação
python src/transcriber_simples.py audio.mp3 \
    --reference "João" joao_amostra.wav \
    --reference "Maria" maria_amostra.wav

# Sem identificação de falantes (mais rápido)
python src/transcriber_simples.py audio.mp3 --no-identify
```

### Via Python

```python
from src.transcriber_simples import AudioTranscriber

# Cria o transcritor
transcriber = AudioTranscriber(language="pt")

# Opcional: Registra amostras de referência
transcriber.register_reference("João", "joao_amostra.wav")
transcriber.register_reference("Maria", "maria_amostra.wav")

# Processa o áudio
resultados = transcriber.process("audio.mp3")

# Salva relatório
arquivos = transcriber.save_report(resultados, formats=["txt", "md"])

# Acessa resultados
print(f"Texto completo: {resultados['full_text']}")
print(f"Segmentos: {len(resultados['segments'])}")

for seg in resultados['segments']:
    falante = seg['identified_as'] or seg['speaker']
    print(f"[{falante}] {seg['text']}")
```

## Parâmetros Disponíveis

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--min-speakers` | Número mínimo de falantes | 1 |
| `--max-speakers` | Número máximo de falantes | 5 |
| `--language` | Idioma (pt, en, es, etc.) | pt |
| `--device` | cpu ou cuda | auto-detect |
| `--output-dir` | Diretório de saída | output |
| `--reference` | Amostra de referência (nome, arquivo) | None |
| `--no-identify` | Desativa identificação | False |

## Saída

O transcritor gera:
- **TXT**: Transcrição em texto simples
- **MD**: Relatório formatado em Markdown
- **HTML**: Relatório visual navegável

Exemplo de saída TXT:
```
======================================================================
TRANSCRIÇÃO DE ÁUDIO
======================================================================
Arquivo: audio.mp3
Data: 2024-01-15T10:30:00
Duração: 125.5s
----------------------------------------------------------------------

[00:00.000] João:
  Olá, bom dia!

[00:05.200] Maria:
  Bom dia! Como você está?

======================================================================
```

## Vantagens desta Versão Simplificada

1. **Código mais limpo**: ~550 linhas vs ~600+ da versão original
2. **Menos dependências**: Foco no essencial
3. **Lazy loading**: Modelos carregados sob demanda
4. **Melhor tratamento de erros**: Mensagens claras e objetivas
5. **Interface CLI intuitiva**: Fácil de usar e automatizar
6. **Sem Gradio**: Remove complexidade desnecessária para uso básico

## Requisitos do Sistema

- Python 3.8+
- 4GB RAM mínimo (8GB recomendado)
- GPU CUDA opcional (acelera processamento)
- ffmpeg instalado no sistema

## Solução de Problemas

### Erro: "Token necessário"
```bash
export HUGGINGFACE_TOKEN="hf_seu_token_aqui"
```

### Erro: "CUDA out of memory"
Use CPU ou reduza tamanho do áudio:
```bash
python src/transcriber_simples.py audio.mp3 --device cpu
```

### Erro: "ffmpeg não encontrado"
Instale o ffmpeg:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

# macOS (Homebrew)
brew install ffmpeg
```

## Licença

MIT License - mesmo license do projeto original.
