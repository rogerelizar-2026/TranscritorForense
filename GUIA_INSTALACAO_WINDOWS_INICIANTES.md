# 📘 GUIA DE INSTALAÇÃO PARA INICIANTES - WINDOWS 11
## Transcritor Forense de Áudio

Este guia foi feito para pessoas **SEM experiência com programação**. Siga cada passo cuidadosamente.

---

## ⏱️ Tempo Estimado
- Instalação completa: **30-45 minutos**
- Dependendo da velocidade da sua internet

---

## 📋 O QUE VOCÊ VAI PRECISAR BAIXAR

1. **Python** (linguagem de programação que o sistema usa)
2. **Git** (programa para baixar o código do sistema)
3. **Conta no Hugging Face** (site gratuito para acessar os modelos de inteligência artificial)

---

## 🚀 PASSO 1: INSTALAR O PYTHON

O Python é como um "motor" que faz o sistema funcionar.

### 1.1 Baixar o Python
1. Abra seu navegador (Chrome, Edge, Firefox)
2. Digite na barra de endereços: `https://www.python.org/downloads/`
3. Pressione **Enter**
4. Você verá um botão amarelo escrito **"Download Python 3.x.x"** (o número pode variar)
5. Clique nesse botão para baixar

### 1.2 Instalar o Python
1. Vá até a pasta **Downloads** do seu computador
2. Dê dois cliques no arquivo que você acabou de baixar (algo como `python-3.12.x.exe`)
3. ⚠️ **MUITO IMPORTANTE:** Na primeira tela que abrir, MARQUE a caixinha na parte inferior:
   ```
   ☑ Add Python to PATH
   ```
   **Se você não marcar isso, o sistema não vai funcionar!**
4. Agora clique em **"Install Now"**
5. Aguarde a instalação terminar (pode levar 2-3 minutos)
6. Quando aparecer "Setup was successful", clique em **"Close"**

### 1.3 Verificar se o Python foi instalado corretamente
1. Pressione as teclas **Windows + R** no teclado
2. Digite `cmd` e pressione **Enter**
3. Uma tela preta vai abrir (Prompt de Comando)
4. Digite o seguinte comando e pressione Enter:
   ```
   python --version
   ```
5. Deve aparecer algo como: `Python 3.12.x`
   - ✅ Se apareceu o número da versão: **CORRETO! Pode continuar**
   - ❌ Se apareceu "não é reconhecido": Volte ao passo 1.2 e reinstale marcando "Add Python to PATH"

---

## 🚀 PASSO 2: INSTALAR O GIT

O Git é um programa que baixa o código do sistema do GitHub.

### 2.1 Baixar o Git
1. No seu navegador, digite: `https://git-scm.com/download/win`
2. Pressione **Enter**
3. O download deve começar automaticamente
4. Se não começar, clique no link **"64-bit Git for Windows Setup"**

### 2.2 Instalar o Git
1. Vá até a pasta **Downloads**
2. Dê dois cliques no arquivo baixado (algo como `Git-2.x.x-64-bit.exe`)
3. Vá clicando em **"Next"** em todas as telas
4. Pode aceitar todas as opções padrão
5. Na tela "Choosing the default editor", pode deixar como está e clicar **Next**
6. Continue clicando **Next** até chegar em **Install**
7. Clique em **Install** e aguarde
8. Quando terminar, clique em **Finish**

---

## 🚀 PASSO 3: BAIXAR O SISTEMA TRANSCRITOR FORENSE

Agora vamos baixar o código do sistema.

### 3.1 Criar uma pasta para o projeto
1. Abra o **Explorador de Arquivos** (ícone de pastinha amarela)
2. No lado esquerdo, clique em **Área de Trabalho** ou **Documentos**
3. Clique com o botão direito em um espaço vazio
4. Selecione **Novo** → **Pasta**
5. Nomeie a pasta como: `projetos`
6. Dê dois cliques para entrar nessa pasta

### 3.2 Baixar o código do sistema
1. Dentro da pasta `projetos`, clique com o botão direito em um espaço vazio
2. Selecione **"Abrir no Terminal"** ou **"Open in Terminal"**
   - Se não aparecer essa opção, segure a tecla **Shift** e clique com o botão direito, depois escolha **"Abrir janela do PowerShell aqui"**
3. Uma tela azul ou preta vai abrir
4. Digite o seguinte comando EXATO e pressione **Enter**:
   ```
   git clone https://github.com/SEU_USUARIO/transcritor-forense.git
   ```
   ⚠️ **ATENÇÃO:** Substitua `SEU_USUARIO` pelo nome real do usuário/repositório no GitHub onde o código está hospedado.
   
   Se você não sabe o URL exato, peça para quem desenvolveu o sistema te fornecer o link correto.

5. Aguarde o download terminar. Você verá mensagens aparecendo na tela.

### 3.3 Entrar na pasta do sistema
Na mesma tela do terminal, digite:
```
cd transcritor-forense
```
Pressione **Enter**

---

## 🚀 PASSO 4: CRIAR AMBIENTE VIRTUAL

Um ambiente virtual é como uma "caixa separada" só para este sistema, para não bagunçar outras coisas no seu computador.

### 4.1 Criar o ambiente
Na mesma tela do terminal (certifique-se de estar dentro da pasta `transcritor-forense`), digite:
```
python -m venv venv
```
Pressione **Enter**

Isso vai criar uma nova pasta chamada `venv` dentro do projeto. Pode levar 1-2 minutos.

### 4.2 Ativar o ambiente virtual
Agora digite:
```
venv\Scripts\activate
```
Pressione **Enter**

✅ **Como saber se funcionou:** Você deve ver `(venv)` aparecendo no início da linha do terminal, assim:
```
(venv) C:\Users\SeuNome\projetos\transcritor-forense>
```

---

## 🚀 PASSO 5: INSTALAR AS DEPENDÊNCIAS

As dependências são como "peças" que o sistema precisa para funcionar.

### 5.1 Atualizar o instalador
No terminal (com `(venv)` aparecendo), digite:
```
python -m pip install --upgrade pip
```
Pressione **Enter**

### 5.2 Instalar todas as peças necessárias
Agora digite:
```
pip install -r requirements.txt
```
Pressione **Enter**

⏱️ **Isso vai demorar!** Pode levar de 10 a 20 minutos dependendo da sua internet.

Você verá muitas mensagens aparecendo:
- `Collecting...`
- `Downloading...`
- `Installing...`

**Não se assuste!** É normal. Apenas aguarde até voltar a aparecer o `(venv)` no final.

❗ **Se der erro:** 
- Verifique se você está conectado à internet
- Tente executar o comando novamente
- Se persistir, reinicie o computador e tente do passo 4.2 em diante

---

## 🚀 PASSO 6: OBTER TOKEN DO HUGGING FACE (OBRIGATÓRIO)

O Hugging Face é um site que fornece os "cérebros" de inteligência artificial que o sistema usa. Você precisa criar uma conta gratuita e pegar uma "chave de acesso" (token).

### 6.1 Criar conta no Hugging Face
1. Abra seu navegador
2. Digite: `https://huggingface.co`
3. Pressione **Enter**
4. No canto superior direito, clique em **"Sign Up"**
5. Preencha:
   - Seu email
   - Uma senha
   - Um nome de usuário (username)
6. Clique em **"Sign Up"**
7. Vá até seu email e clique no link de confirmação que você receberá

### 6.2 Aceitar os termos dos modelos
Você precisa autorizar o uso de DOIS modelos:

**Modelo 1:**
1. No navegador, digite: `https://huggingface.co/pyannote/speaker-diarization-3.1`
2. Role a página para baixo até encontrar um botão
3. Clique em **"Agree and access repository"**

**Modelo 2:**
1. No navegador, digite: `https://huggingface.co/pyannote/segmentation-3.0`
2. Clique em **"Agree and access repository"**

### 6.3 Gerar o token
1. No navegador, digite: `https://huggingface.co/settings/tokens`
2. Clique no botão **"New token"**
3. Dê um nome para o token, por exemplo: `transcritor`
4. Em "Type", selecione: **"Read"** (leitura)
5. Clique em **"Generate token"**
6. **COPIE O TOKEN!** Ele começa com `hf_` seguido de várias letras e números
   - Exemplo: `hf_AbCdEfGhIjKlMnOpQrStUvWxYz123456`
   - ⚠️ **Atenção:** Você só consegue ver o token completo uma vez! Copie agora!

### 6.4 Configurar o token no sistema
1. Abra o **Explorador de Arquivos**
2. Navegue até: `Área de Trabalho\projetos\transcritor-forense` (ou onde você instalou)
3. Procure um arquivo chamado `config.yaml`
4. Clique com o botão direito nele e selecione **"Abrir com"** → **Bloco de Notas**
5. Você verá algo assim:
   ```yaml
   huggingface_token: "hf_seu_token_aqui"
   ```
6. Apague `hf_seu_token_aqui` e cole o token que você copiou (mantenha as aspas!)
   - Deve ficar assim: `huggingface_token: "hf_AbCdEfGhIjKlMnOpQrStUvWxYz123456"`
7. No Bloco de Notas, clique em **Arquivo** → **Salvar**
8. Feche o Bloco de Notas

---

## 🚀 PASSO 7: TESTAR A INSTALAÇÃO

Vamos verificar se tudo foi instalado corretamente.

### 7.1 Abrir o terminal novamente
1. Pressione **Windows**, digite `cmd` e pressione **Enter**
2. Digite os comandos abaixo, pressionando **Enter** após cada um:

```
cd %USERPROFILE%\projetos\transcritor-forense
```

```
venv\Scripts\activate
```

Você deve ver `(venv)` aparecer no início da linha.

### 7.2 Rodar o teste
Digite:
```
python tests\test_formatter_standalone.py
```
Pressione **Enter**

✅ **Se aparecer `OK` no final:** Parabéns! A instalação básica está correta!
❌ **Se aparecer erro:** Alguma coisa deu errado. Revise os passos anteriores.

---

## 🚀 PASSO 8: USAR O SISTEMA PELA PRIMEIRA VEZ

### 8.1 Iniciar o sistema
No terminal (com `(venv)` ativo e dentro da pasta do projeto), digite:
```
python -m src.app
```
Pressione **Enter**

Aguarde alguns segundos. Você verá mensagens como:
```
Running on local URL: http://localhost:7860
```

### 8.2 Abrir no navegador
1. Abra seu navegador (Chrome, Edge, Firefox)
2. Na barra de endereços, digite: `http://localhost:7860`
3. Pressione **Enter**

✅ **Se aparecer uma interface web:** PARABÉNS! O sistema está funcionando!

---

## 📖 COMO USAR O SISTEMA

Agora que está aberto no navegador:

### Para transcrever um áudio:

1. **Carregar o áudio:**
   - Clique em **"Browse files"** na seção "Upload de Áudio"
   - Selecione seu arquivo de áudio (WAV, MP3, etc.)
   - Aguarde carregar

2. **(Opcional) Carregar amostras de voz:**
   - Se você tiver gravações curtas de cada pessoa falando separadamente, pode carregar aqui
   - Isso ajuda o sistema a identificar quem é cada um automaticamente

3. **Configurar:**
   - Número de falantes: coloque quantas pessoas participam da conversa (geralmente 2)
   - Idioma: deixe como "pt" (português)

4. **Processar:**
   - Clique em **"🔄 Processar Áudio"**
   - ⏱️ **Aguarde:** Sem placa de vídeo NVIDIA, isso pode levar 5-10 minutos para cada minuto de áudio
   - Não feche a janela!

5. **Revisar:**
   - O sistema vai mostrar quem falou o quê e quando
   - Você pode editar os nomes (ex: mudar "SPEAKER_00" para "Cliente")

6. **Gerar relatório:**
   - Clique em **"📄 Gerar Relatório Forense"**
   - O sistema vai criar arquivos em vários formatos (HTML, TXT, Markdown)
   - Esses arquivos serão salvos na pasta `output` dentro do projeto

---

## ⚠️ PROBLEMAS COMUNS E SOLUÇÕES

### ❌ "python não é reconhecido como um comando interno"
**Solução:** Reinstale o Python e NÃO ESQUEÇA de marcar "Add Python to PATH" na instalação.

### ❌ Erro ao instalar dependências
**Solução:** 
1. Verifique se está conectado à internet
2. Certifique-se de que o `(venv)` aparece no terminal
3. Tente rodar novamente: `pip install -r requirements.txt`

### ❌ Token inválido
**Solução:**
1. Verifique se você copiou o token completo (começa com `hf_`)
2. Confira se colou corretamente no arquivo `config.yaml` (mantenha as aspas!)
3. Verifique se aceitou os termos nos dois links do passo 6.2

### ❌ Sistema muito lento
**Solução:** Isso é normal sem placa de vídeo dedicada. Deixe o sistema trabalhando e faça outra coisa enquanto processa. Evite usar outros programas pesados durante a transcrição.

### ❌ Erro ao abrir no navegador
**Solução:**
1. Verifique se o terminal ainda está aberto mostrando `Running on local URL`
2. Tente fechar e abrir novamente seguindo o passo 8.1
3. Se necessário, reinicie o computador e comece do passo 8.1

---

## 💾 COMO FECHAR E ABRIR NOVAMENTE NO FUTURO

### Para fechar:
- No terminal onde o sistema está rodando, pressione **Ctrl + C** no teclado
- Ou simplesmente feche a janela do terminal

### Para abrir novamente no futuro:
1. Pressione **Windows**, digite `cmd` e pressione **Enter**
2. Digite estes comandos (um por um, pressionando Enter após cada):
   ```
   cd %USERPROFILE%\projetos\transcritor-forense
   venv\Scripts\activate
   python -m src.app
   ```
3. Abra o navegador em `http://localhost:7860`

---

## 📞 PRECISA DE MAIS AJUDA?

Se você seguiu todos os passos e ainda está com problemas:
1. Anote a mensagem de erro exata que aparece
2. Tire uma foto da tela
3. Entre em contato com o suporte técnico ou com quem te forneceu este sistema

---

## ✅ RESUMO RÁPIDO (PARA CONSULTA FUTURA)

Sempre que quiser usar o sistema:

1. Abra o Prompt de Comando (Windows + R, digite `cmd`, Enter)
2. Digite:
   ```
   cd %USERPROFILE%\projetos\transcritor-forense
   venv\Scripts\activate
   python -m src.app
   ```
3. Abra o navegador em `http://localhost:7860`
4. Use o sistema!

---

**Parabéns por chegar até aqui!** 🎉
Agora você tem uma ferramenta profissional de transcrição forense no seu computador!
