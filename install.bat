@echo off
REM =============================================================================
REM INSTALADOR AUTOMÁTICO - TRANSCRITOR FORENSE DE ÁUDIO (Windows)
REM =============================================================================
REM Este script automatiza toda a instalação do sistema, deixando-o pronto para uso.
REM Compatível com Windows 10/11
REM Versão: 2.0.0 (Corrigida e Otimizada)
REM =============================================================================

echo.
echo =============================================================================
echo   ||  INSTALADOR AUTOMATICO - TRANSCRITOR FORENSE DE AUDIO
echo       Versao 2.0.0 - Compativel com Python 3.10 a 3.12
echo =============================================================================
echo.
echo [INFO] Este instalador configurara todo o ambiente necessario para uso do sistema.
echo.

REM Verificar se esta na pasta correta
if not exist "requirements.txt" (
    echo [ERRO] Execute este script no diretorio raiz do projeto
    pause
    exit /b 1
)

if not exist "config.yaml" (
    echo [ERRO] Arquivo config.yaml nao encontrado
    pause
    exit /b 1
)

REM Passo 1: Verificar Python
echo [PASSO 1/8] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado. Instale Python 3.10 ou superior.
    echo [INFO] Baixe em: https://www.python.org/downloads/
    echo [INFO] Marque a opcao 'Add Python to PATH' durante a instalacao.
    pause
    exit /b 1
)

python --version
echo [SUCESSO] Python OK
echo.

REM Passo 2: Criar ambiente virtual
echo [PASSO 2/8] Criando ambiente virtual...
if exist "venv" (
    echo [ATENCAO] Ambiente virtual ja existe. Removendo...
    rmdir /s /q venv
)

python -m venv venv
if errorlevel 1 (
    echo [ERRO] Falha ao criar ambiente virtual
    pause
    exit /b 1
)
echo [SUCESSO] Ambiente virtual criado
echo.

REM Passo 3: Ativar ambiente virtual e atualizar pip
echo [PASSO 3/8] Ativando ambiente e atualizando pip...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel --quiet
echo [SUCESSO] Pip e ferramentas atualizados
echo.

REM Passo 4: Instalar dependências do sistema (FFmpeg)
echo [PASSO 4/8] Verificando FFmpeg...
where ffmpeg >nul 2>&1
if errorlevel 1 (
    echo [ATENCAO] FFmpeg nao encontrado. Instalacao recomendada.
    echo.
    echo [INFO] Para instalar FFmpeg no Windows:
    echo   1. Baixe de: https://www.gyan.dev/ffmpeg/builds/
    echo   2. Extraia o arquivo ZIP
    echo   3. Copie a pasta 'bin' para C:\ffmpeg\bin
    echo   4. Adicione C:\ffmpeg\bin ao PATH do sistema
    echo      - Painel de Controle ^> Sistema ^> Configuracoes avancas ^> Variaveis de Ambiente
    echo      - Edite a variavel 'Path' e adicione o caminho
    echo.
    set /p INSTALL_FFMPEG="Deseja pular esta etapa e continuar mesmo assim? (S/N): "
    if /i "%INSTALL_FFMPEG%"=="N" (
        echo [INFO] Consulte o manual para instrucoes de instalacao do FFmpeg
        pause
        exit /b 1
    )
    echo [INFO] Continuando sem FFmpeg. Algumas funcionalidades podem nao funcionar.
) else (
    echo [SUCESSO] FFmpeg ja instalado
)
echo.

REM Passo 5: Instalar PyTorch primeiro
echo [PASSO 5/8] Instalando PyTorch (biblioteca principal)...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar PyTorch
    pause
    exit /b 1
)
echo [SUCESSO] PyTorch instalado
echo.

REM Passo 5.5: Instalar huggingface_hub com versão compatível
echo [PASSO 5.5/8] Instalando Hugging Face Hub...
pip install "huggingface_hub>=0.20.0,<0.26.0" --quiet
if errorlevel 1 (
    echo [ERRO] Falha ao instalar huggingface_hub
    pause
    exit /b 1
)
echo [SUCESSO] Hugging Face Hub instalado
echo.

REM Passo 6: Instalar demais dependências Python
echo [PASSO 6/8] Instalando dependencias Python (pode demorar 5-15 minutos)...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias
    echo [INFO] Tente executar: pip install --upgrade pip
    pause
    exit /b 1
)
echo [SUCESSO] Dependencias Python instaladas
echo.

REM Passo 7: Criar diretórios necessários
echo [PASSO 7/8] Criando estrutura de diretorios...
if not exist "output" mkdir output
if not exist "samples" mkdir samples
if not exist "models" mkdir models
if not exist "templates" mkdir templates
echo [SUCESSO] Diretorios criados
echo.

REM Passo 8: Configurar token Hugging Face
echo [PASSO 8/8] Configurando token Hugging Face...
echo.
echo =============================================================================
echo   CONFIGURACAO DO HUGGING FACE
echo =============================================================================
echo.
echo [INFO] Os modelos pyannote.audio exigem um token do Hugging Face (gratuito).
echo.
echo [INFO] Siga estas instrucoes:
echo   1. Acesse: https://huggingface.co/join (crie conta se nao tiver)
echo   2. Aceite os termos dos modelos:
echo      - https://huggingface.co/pyannote/speaker-diarization-3.1
echo      - https://huggingface.co/pyannote/segmentation-3.0
echo   3. Gere um token em: https://huggingface.co/settings/tokens
echo   4. Copie o token (comeca com 'hf_')
echo.

set /p HF_TOKEN="Cole seu token do Hugging Face aqui: "

if "%HF_TOKEN%"=="" (
    echo [ATENCAO] Token nao fornecido. O sistema nao funcionara sem ele.
    echo [INFO] Voce pode configurar manualmente depois editando config.yaml
) else (
    REM Atualizar config.yaml com o token usando PowerShell
    powershell -Command "(Get-Content config.yaml) -replace 'hf_seu_token_aqui', '%HF_TOKEN%' | Set-Content config.yaml"
    echo [SUCESSO] Token configurado em config.yaml
)
echo.

REM Resumo final
echo =============================================================================
echo   INSTALACAO CONCLUIDA!
echo =============================================================================
echo.
echo [SUCESSO] O sistema esta pronto para uso!
echo.
echo Proximos passos:
echo   1. Ative o ambiente virtual:
echo      call venv\Scripts\activate
echo.
echo   2. Execute a aplicacao:
echo      python -m src.app
echo.
echo   3. Acesse no navegador: http://localhost:7860
echo.
echo Ou execute o script de inicializacao rapida:
echo   iniciar.bat
echo.
echo =============================================================================
echo.

REM Criar script de inicialização
(
echo @echo off
echo REM Script de inicializacao rapida
echo.
echo if not exist "venv" ^(
echo     echo Erro: Ambiente virtual nao encontrado. Execute install.bat primeiro.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo call venv\Scripts\activate.bat
echo python -m src.app
) > iniciar.bat

echo [SUCESSO] Script de inicializacao criado: iniciar.bat
echo.
pause
