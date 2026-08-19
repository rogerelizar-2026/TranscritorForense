# Guia de Início Rápido - Transcritor Simplificado

## ⚡ 3 Passos para Começar

### Passo 1: Instalar

```bash
# Clone ou acesse o diretório do projeto
cd /workspace

# Execute o instalador automático
chmod +x install_simples.sh
./install_simples.sh
```

Ou manualmente:
```bash
pip install -r requirements_simples.txt
```

### Passo 2: Configurar Token (Obrigatório)

Obtenha seu token gratuito em: https://huggingface.co/settings/tokens

```bash
export HUGGINGFACE_TOKEN="hf_seu_token_aqui"
```

### Passo 3: Usar

```bash
# Forma mais simples
python src/transcriber_simples.py seu_audio.mp3

# Com opções avançadas
python src/transcriber_simples.py audio.mp3 \
    --min-speakers 2 \
    --max-speakers 4 \
    --reference "João" joao.wav \
    --reference "Maria" maria.wav
```

---

## 📋 Exemplos Práticos

### Transcrição Simples
```bash
python src/transcriber_simples.py reuniao.mp3
```

### Identificar Falantes com Amostras
```bash
python src/transcriber_simples.py entrevista.mp3 \
    --reference "Entrevistador" entrevistador.wav \
    --reference "Entrevistado" entrevistado.wav
```

### Processamento Rápido (sem identificação)
```bash
python src/transcriber_simples.py podcast.mp3 --no-identify
```

### Usando GPU (se disponível)
```bash
python src/transcriber_simples.py audio.mp3 --device cuda
```

---

## 🐍 Uso via Python

```python
from src.transcriber_simples import AudioTranscriber

# Inicializa
t = AudioTranscriber(language="pt")

# Opcional: registra voes de referência
t.register_reference("Ana", "ana_amostra.wav")
t.register_reference("Carlos", "carlos_amostra.wav")

# Processa
resultado = t.process("audio.mp3")

# Salva relatórios
t.save_report(resultado, formats=["txt", "md", "html"])

# Acessa dados
print(f"Falantes: {resultado['speakers']}")
print(f"Segmentos: {len(resultado['segments'])}")

for seg in resultado['segments']:
    nome = seg['identified_as'] or seg['speaker']
    print(f"{nome}: {seg['text']}")
```

---

## 📁 Arquivos Gerados

Após processar `audio.mp3`, você terá na pasta `output/`:

- `audio_transcricao.txt` - Texto simples
- `audio_relatorio.md` - Markdown formatado  
- `audio_relatorio.html` - Página web navegável

---

## ❓ Problemas Comuns

| Erro | Solução |
|------|---------|
| `ModuleNotFoundError` | `pip install -r requirements_simples.txt` |
| `Token necessário` | `export HUGGINGFACE_TOKEN="hf_..."` |
| `ffmpeg não encontrado` | `sudo apt install ffmpeg` (Linux) |
| `CUDA out of memory` | Use `--device cpu` |
| `Arquivo não encontrado` | Verifique o caminho do arquivo |

---

## 🎯 Dicas de Performance

1. **Áudios longos**: Divida em partes menores (< 10 min cada)
2. **GPU disponível**: Use `--device cuda` para 5-10x mais rápido
3. **Sem identificação**: Use `--no-identify` para processamento mais rápido
4. **Modelo menor**: Edite o código para usar `model_name="tiny"` ou `"base"`

---

## 📞 Suporte

- 📖 Leia: `README_SIMPLIFICADO.md`
- 💻 Help: `python src/transcriber_simples.py --help`
- 🐛 Issues: Verifique a documentação original

---

**Versão**: 1.0.0 Simplificada  
**Foco**: Estabilidade e simplicidade
