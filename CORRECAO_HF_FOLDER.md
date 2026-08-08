# 🛠️ Correção de Erro: HfFolder do huggingface_hub

## ❌ Problema Identificado

```
ImportError: cannot import name 'HfFolder' from 'huggingface_hub'
```

Este erro ocorre quando há uma **incompatibilidade de versões** entre o `gradio` e o `huggingface_hub`.

### Causa Raiz

- Versões recentes do `huggingface_hub` (≥0.26.0) removeram ou modificaram a classe `HfFolder`
- O `gradio` versão 4.x ainda depende da `HfFolder` para autenticação OAuth
- Sem especificar a versão correta, o pip instala a versão mais recente do `huggingface_hub`, causando conflito

---

## ✅ Solução Aplicada

### 1. **requirements.txt Atualizado**

Adicionamos uma restrição de versão explícita:

```txt
# Hugging Face - necessário para pyannote, speechbrain e gradio
# Versão compatível com HfFolder (necessário para gradio < 5.0)
huggingface_hub>=0.20.0,<0.26.0
```

### 2. **Instaladores Corrigidos**

#### Windows (`install.bat`)
Adicionado passo específico para instalar `huggingface_hub` antes das demais dependências:

```batch
REM Passo 5.5: Instalar huggingface_hub com versão compatível
echo [PASSO 5.5/8] Instalando Hugging Face Hub...
pip install "huggingface_hub>=0.20.0,<0.26.0" --quiet
```

#### Linux/macOS (`install.sh`)
Mesma correção aplicada:

```bash
log_info "Instalando Hugging Face Hub com versão compatível..."
pip install "huggingface_hub>=0.20.0,<0.26.0" --quiet
```

---

## 🔧 Como Corrigir no Seu Ambiente Atual

Se você já instalou o projeto e está enfrentando este erro, siga estes passos:

### Opção 1: Reinstalação Completa (Recomendado)

1. **Delete o ambiente virtual atual:**
   ```cmd
   rmdir /s /q venv
   ```

2. **Execute o instalador corrigido:**
   ```cmd
   install.bat
   ```

### Opção 2: Correção Rápida (Sem reinstalar tudo)

1. **Ative o ambiente virtual:**
   ```cmd
   call venv\Scripts\activate
   ```

2. **Reinstale o huggingface_hub com a versão correta:**
   ```cmd
   pip install "huggingface_hub>=0.20.0,<0.26.0" --force-reinstall
   ```

3. **Teste a importação:**
   ```cmd
   python -c "from huggingface_hub import HfFolder; print('OK!')"
   ```

4. **Execute o aplicativo:**
   ```cmd
   python -m src.app
   ```

---

## 📋 Versões Compatíveis Testadas

| Pacote | Versão Mínima | Versão Máxima | Motivo |
|--------|--------------|---------------|--------|
| huggingface_hub | 0.20.0 | 0.25.x | Mantém HfFolder disponível |
| gradio | 4.31.0 | 5.x | Funciona com HfFolder |
| torch | 2.3.0 | 2.7.x | Compatibilidade CUDA/CPU |
| pyannote.audio | 3.3.0 | 4.0.x | Usa token (não use_auth_token) |

---

## 🚀 Prevenção Futura

Para evitar problemas similares:

1. **Sempre use os instaladores fornecidos** (`install.bat` ou `install.sh`)
2. **Não atualize pacotes individualmente** sem verificar compatibilidade
3. **Mantenha o requirements.txt atualizado** com ranges de versão adequados
4. **Teste após instalação** com:
   ```cmd
   python -c "import gradio; from huggingface_hub import HfFolder; print('Tudo OK!')"
   ```

---

## 📞 Suporte

Se o problema persistir:

1. Verifique as versões instaladas:
   ```cmd
   pip show huggingface_hub gradio
   ```

2. Force a reinstalação de ambos:
   ```cmd
   pip install --force-reinstall "huggingface_hub>=0.20.0,<0.26.0" "gradio>=4.31.0,<6.0.0"
   ```

3. Consulte o manual completo em `MANUAL_USUARIO.md`

---

**Data da Correção:** 2025-01-XX  
**Versão do Instalador:** 2.0.1+  
**Status:** ✅ Resolvido
