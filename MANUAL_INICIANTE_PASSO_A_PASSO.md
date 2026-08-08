# 📘 Manual de Uso para Iniciantes - Transcritor Forense de Áudio

**Guia completo e simplificado para quem nunca usou a ferramenta antes.**

---

## 🎯 O Que Você Vai Aprender

1. Como **iniciar** o programa depois de instalado
2. Como **usar** a interface gráfica (fácil, igual a um site)
3. Como **transcrever** seu primeiro áudio
4. Como **baixar** o resultado formatado
5. Exemplos práticos do dia a dia

---

## ⚡ Resumo Rápido (Para Quem Tem Pressa)

```bash
# 1. Abra o terminal na pasta onde instalou
cd /workspace

# 2. Inicie o programa
python src/app.py

# 3. O programa vai mostrar um endereço como: http://127.0.0.1:7860
# 4. Abra esse endereço no seu navegador (Chrome, Firefox, etc.)
# 5. Use a interface visual para carregar áudios e transcrever
```

**Tempo estimado:** 5 minutos para iniciar + tempo de processamento do áudio

---

## 📖 Passo a Passo Detalhado

### PASSO 1: Verificando se Tudo Está Instalado

Antes de começar, vamos confirmar que a instalação foi bem-sucedida.

**No Windows:**
1. Pressione `Windows + R`
2. Digite `cmd` e pressione Enter
3. Digite: `cd C:\caminho\da\sua\instalacao` (substitua pelo caminho real)
4. Digite: `python --version` → Deve aparecer Python 3.10 ou superior

**No Linux/Mac:**
1. Abra o Terminal
2. Digite: `cd /caminho/da/sua/instalacao`
3. Digite: `python3 --version` → Deve aparecer Python 3.10 ou superior

✅ **Se apareceu a versão do Python:** Pode continuar!  
❌ **Se deu erro "python não encontrado":** Volte ao guia de instalação.

---

### PASSO 2: Iniciando o Programa

O Transcritor Forense funciona como um **site local** no seu computador. Você precisa "ligar o servidor" primeiro.

#### No Windows:

**Opção A - Usando o ícone (se criou atalho):**
- Dê dois cliques no arquivo `INICIAR_PROGRAMA.bat`

**Opção B - Manualmente:**
1. Abra o Prompt de Comando (digite "cmd" no menu Iniciar)
2. Navegue até a pasta: `cd C:\caminho\da\instalacao`
3. Digite: `python src\app.py`
4. Pressione Enter

#### No Linux/Mac:

1. Abra o Terminal
2. Navegue até a pasta: `cd /caminho/da/instalacao`
3. Digite: `python3 src/app.py`
4. Pressione Enter

---

### PASSO 3: Acessando a Interface Gráfica

Depois de executar o comando, você verá mensagens parecidas com estas:

```
Running on local URL: http://127.0.0.1:7860
Running on public URL: https://xxx-xxx-xxx.gradio.live
```

**O que fazer:**

1. **Copie** o endereço que aparece (geralmente `http://127.0.0.1:7860`)
2. **Abra** seu navegador (Chrome, Firefox, Edge, Safari)
3. **Cole** o endereço na barra de endereços
4. **Pressione** Enter

✅ **Pronto!** Agora você está vendo a interface do programa!

> **Dica:** Não feche a janela do terminal enquanto estiver usando o programa. Ela precisa ficar aberta.

---

### PASSO 4: Conhecendo a Interface

A tela principal tem **4 áreas principais**:

```
┌─────────────────────────────────────────────┐
│  🎤 CARREGAR ÁUDIO                          │
│  [Arraste seu arquivo aqui ou clique]       │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  👥 FALANTES                                │
│  Número mínimo: [2]  Número máximo: [5]     │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  🔘 TRANSCREVER                             │
│  [Botão Grande Azul]                        │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│  📄 RESULTADO                               │
│  [Aqui aparece a transcrição]               │
│  [Baixar MD] [Baixar TXT] [Baixar HTML]     │
└─────────────────────────────────────────────┘
```

---

### PASSO 5: Transcrevendo Seu Primeiro Áudio

Vamos fazer um teste prático!

#### 5.1 Preparando o Áudio

**Formatos aceitos:**
- ✅ WAV (melhor qualidade)
- ✅ MP3 (mais comum)
- ✅ FLAC, M4A, OGG

**Recomendações:**
- Áudio deve estar em **português**
- Evite ruídos muito altos
- Duração: até 30 minutos para testes (pode demorar)

#### 5.2 Carregando o Áudio

1. Na área **"CARREGAR ÁUDIO"**, você tem duas opções:
   - **Arrastar:** Pegue o arquivo do seu computador e arraste para dentro da área
   - **Clicar:** Clique na área e selecione o arquivo nas suas pastas

2. Aguarde o carregamento (aparece uma barrinha de progresso)

3. Quando terminar, você verá o nome do arquivo listado

#### 5.3 Configurando os Falantes

Na área **"FALANTES"**:

- **Número mínimo de falantes:** Quantas pessoas você acha que têm no áudio
  - Exemplo: Se é uma ligação entre cliente e atendente → coloque `2`
  
- **Número máximo de falantes:** Limite superior
  - Exemplo: Se pode ter mais gente entrando → coloque `5`

> **Dica:** Se não sabe, deixe 2 e 5. O programa detecta automaticamente.

#### 5.4 Iniciando a Transcrição

1. Clique no botão **"TRANSCREVER"** (botão grande azul)

2. **Aguarde o processamento** - isso pode levar:
   - **Com GPU (placa de vídeo):** 1-2 minutos por hora de áudio
   - **Sem GPU (só processador):** 5-10 minutos por hora de áudio

3. Durante o processamento, você verá:
   ```
   ⏳ Processando... (isso pode demorar alguns minutos)
   ```

4. **Não feche a janela!** Deixe trabalhando.

---

### PASSO 6: Lendo o Resultado

Quando terminar, aparece algo assim na área **"RESULTADO"**:

```
======================================
RELATÓRIO DE TRANSCRIÇÃO FORENSE
======================================
Arquivo: negociacao_cliente.wav
Hash: a1b2c3d4e5f6...
Data: 2025-08-08 14:30:00
--------------------------------------
TRANSCRIÇÃO
--------------------------------------

[00:00.123] Atendente: Bom dia, em que posso ajudar?

[00:05.456] Cliente: Olá, gostaria de saber sobre meu contrato...

[00:12.789] Atendente: Claro, vou verificar aqui...

[00:20.012] Cliente: O número do protocolo é 12345...

======================================
Transcritor Forense v1.0.0
======================================
```

**O que significa:**

- `[00:00.123]` → **Timestamp**: Momento exato em que foi dito (minuto:segundo.milissegundo)
- `Atendente:` → **Quem falou**: Identificação do falante
- `Bom dia...` → **O que foi dito**: Texto transcrito

---

### PASSO 7: Baixando o Resultado

Você tem **3 formatos** disponíveis:

#### 📄 Formato Markdown (.md)
- **Use para:** Documentos técnicos, GitHub, Notion
- **Vantagem:** Formatação rica, fácil de ler
- **Botão:** `[Baixar MD]`

#### 📝 Formato Texto (.txt)
- **Use para:** Enviar por email, abrir no Bloco de Notas
- **Vantagem:** Compatível com qualquer programa
- **Botão:** `[Baixar TXT]`

#### 🌐 Formato HTML (.html)
- **Use para:** Visualizar no navegador, imprimir bonito
- **Vantagem:** Visual profissional, parece um relatório
- **Botão:** `[Baixar HTML]`

**Como baixar:**
1. Clique no botão do formato desejado
2. Escolha onde salvar no seu computador
3. Pronto! Arquivo baixado ✅

---

## 🎓 Exemplos Práticos do Dia a Dia

### EXEMPLO 1: Ligação de Cobrança

**Situação:** Você recebeu uma ligação de cobrança e quer documentar o que foi dito.

**Passos:**
1. Grave a ligação (formato MP3 ou WAV)
2. Salve como `cobranca_2025_08_08.wav`
3. Siga os passos acima para transcrever
4. Baixe em formato TXT para anexar no processo

**Resultado esperado:**
```
[00:00.500] Cobrador: Alô, falo com João Silva?

[00:03.200] Você: Sim, sou eu.

[00:05.100] Cobrador: Aqui é da empresa X, sobre sua dívida...
```

---

### EXEMPLO 2: Negociação com Banco

**Situação:** Você negociou uma dívida com o banco e quer provar o que foi prometido.

**Passos:**
1. Grave a ligação durante a negociação
2. Transcreva usando a ferramenta
3. Baixe em formato HTML (visual profissional)
4. Imprima e guarde com seus documentos

**Dica extra:** Anote o número do protocolo e mencione durante a gravação!

---

### EXEMPLO 3: Reunião Familiar (Guarda de Filhos)

**Situação:** Em processo de guarda, você tem áudios de conversas importantes.

**Passos:**
1. Selecione os áudios relevantes
2. Configure para 2 falantes (mãe e pai, por exemplo)
3. Transcreva cada áudio separadamente
4. Baixe todos em formato MD para organizar

**Importante:** Mantenha os arquivos originais guardados!

---

## ❓ Perguntas Frequentes

### "Demorou muito e não terminou"

**Causas possíveis:**
- Áudio muito longo (+1 hora)
- Computador sem placa de vídeo
- Muitos falantes simultâneos

**Soluções:**
- Divida áudios longos em partes menores
- Tenha paciência (pode levar 10+ minutos)
- Use à noite se estiver usando o computador para outras coisas

---

### "Apareceu erro ao carregar"

**Verifique:**
1. O arquivo é realmente áudio? (MP3, WAV, etc.)
2. O arquivo não está corrompido?
3. O nome do arquivo tem caracteres especiais? (evite ç, ã, @, #)

**Solução:** Renomeie para algo simples como `audio1.wav`

---

### "Os falantes ficaram trocados"

**Isso é normal!** O programa identifica vozes diferentes, mas não sabe os nomes.

**Solução:** Depois de transcrever, você pode editar manualmente o arquivo:
- Onde diz `Falante 1`, substitua por `João`
- Onde diz `Falante 2`, substitua por `Maria`

---

### "Não entendi o que foi dito"

**Possíveis causas:**
- Áudio com muito ruído
- Pessoa falando muito baixo
- Sotaque muito forte

**Soluções:**
- Use áudios de melhor qualidade
- Peça para falar mais claro em futuras gravações
- Revise manualmente a transcrição

---

### "Posso usar no celular?"

**Resposta:** Não diretamente. O programa roda no computador.

**Alternativa:**
1. Transfira os áudios do celular para o computador
2. Transcreva no computador
3. Envie o resultado de volta para o celular

---

## 🔧 Problemas Comuns e Soluções

| Problema | Causa Provável | Solução |
|----------|----------------|---------|
| "Python não encontrado" | Python não instalado ou não está no PATH | Reinstale Python marcando "Add to PATH" |
| "Porta 7860 já em uso" | Outro programa usando a mesma porta | Feche outros programas ou reinicie o PC |
| "Erro de memória" | Áudio muito longo | Divida o áudio em partes menores |
| "Navegador não abre" | Firewall bloqueando | Tente outro navegador ou desative temporariamente o firewall |
| "Transcrição errada" | Áudio com ruído ou idioma errado | Melhore qualidade do áudio ou verifique se está em português |

---

## 💡 Dicas de Ouro

1. **Sempre guarde o áudio original** - Ele é sua prova primária
2. **Faça backup dos resultados** - Salve em nuvem (Google Drive, OneDrive)
3. **Teste com áudios curtos primeiro** - Antes de transcrever horas de áudio
4. **Revise sempre a transcrição** - IA pode errar palavras técnicas ou nomes próprios
5. **Use fones de ouvido** - Para revisar o áudio enquanto lê a transcrição

---

## 🆘 Preciso de Ajuda!

Se nada funcionou:

1. **Releia este manual** - Muitas respostas estão aqui
2. **Verifique os logs** - A janela do terminal mostra erros detalhados
3. **Consulte o README.md** - Documentação técnica completa
4. **Procure ajuda especializada** - Grupos de usuário, fóruns

---

## 📞 Checklist Final

Antes de começar, confirme:

- [ ] Python 3.10+ instalado
- [ ] Arquivos de áudio preparados (WAV ou MP3)
- [ ] Espaço em disco suficiente (10 GB livres)
- [ ] Navegador atualizado (Chrome, Firefox, etc.)
- [ ] Paciência para esperar o processamento 😊

---

## 🎉 Parabéns!

Agora você sabe:
- ✅ Como iniciar o programa
- ✅ Como usar a interface gráfica
- ✅ Como transcrever áudios
- ✅ Como baixar os resultados
- ✅ Como resolver problemas comuns

**Boa sorte com suas transcrições!**

---

*Documento criado para usuários iniciantes - Versão 1.0*  
*Última atualização: Agosto 2025*
