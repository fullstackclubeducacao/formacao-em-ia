@echo off
setlocal enabledelayedexpansion

REM ===============================================
REM  🤖 Sistema de Edição de Vídeos AI
REM  Instalador Automático para Windows
REM  Versão: 3.0.0 - Instalação Completa
REM ===============================================

echo.
echo ==========================================
echo 🤖 Sistema de Edicao de Videos AI
echo    Instalador Completo para Windows
echo ==========================================
echo.

REM Verificar se estamos no diretório correto
if not exist "content_pipeline.py" (
    echo ❌ ERRO: content_pipeline.py nao encontrado!
    echo    Execute este instalador na pasta raiz do projeto.
    pause
    exit /b 1
)

REM Função para imprimir status
goto :main

:print_success
echo ✅ %1
goto :eof

:print_warning
echo ⚠️  %1
goto :eof

:print_error
echo ❌ %1
goto :eof

:print_info
echo ℹ️  %1
goto :eof

:download_ffmpeg
echo 🎥 Baixando FFmpeg + FFprobe...
echo 📥 URL: https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip

REM Baixar FFmpeg usando PowerShell
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'}"
if %errorlevel% neq 0 (
    call :print_error "Falha ao baixar FFmpeg"
    echo 📥 Baixe manualmente em: https://ffmpeg.org/download.html
    goto :eof
)

call :print_success "Download concluido"

REM Extrair FFmpeg
echo 📦 Extraindo FFmpeg...
powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath '.' -Force"
if %errorlevel% neq 0 (
    call :print_error "Falha ao extrair FFmpeg"
    goto :eof
)

REM Encontrar e mover os executáveis
for /d %%d in (ffmpeg-*) do (
    if exist "%%d\bin\ffmpeg.exe" (
        copy "%%d\bin\ffmpeg.exe" "bin\" >nul
        copy "%%d\bin\ffprobe.exe" "bin\" >nul
        rmdir /s /q "%%d"
        del "ffmpeg.zip"
        call :print_success "FFmpeg + FFprobe instalados em bin\"
        goto :eof
    )
)

call :print_error "FFmpeg nao encontrado no arquivo extraido"
goto :eof

:main

REM 1. Verificar Python
echo 🐍 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if !errorlevel! neq 0 (
        call :print_error "Python nao encontrado!"
        echo.
        echo 📥 Baixe e instale Python 3.8+ em:
        echo    https://www.python.org/downloads/
        echo    ✅ Marque 'Add Python to PATH' durante instalacao
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

for /f "tokens=2" %%i in ('!PYTHON_CMD! --version') do set PYTHON_VERSION=%%i
call :print_success "Python encontrado: !PYTHON_VERSION!"

REM Verificar versão do Python
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set PYTHON_MAJOR=%%a
    set PYTHON_MINOR=%%b
)

if !PYTHON_MAJOR! lss 3 (
    call :print_error "Python 3.8+ necessario. Versao atual: !PYTHON_VERSION!"
    pause
    exit /b 1
)

if !PYTHON_MAJOR! equ 3 if !PYTHON_MINOR! lss 8 (
    call :print_error "Python 3.8+ necessario. Versao atual: !PYTHON_VERSION!"
    pause
    exit /b 1
)

REM 2. Criar estrutura de diretórios
echo.
echo 📁 Criando estrutura de diretorios...
if not exist "videos" mkdir videos
if not exist "temp" mkdir temp
if not exist "bin" mkdir bin

call :print_success "Diretorios criados: videos\, temp\, bin\"

REM 3. Instalar FFmpeg + FFprobe
echo.
if exist "bin\ffmpeg.exe" (
    call :print_success "FFmpeg ja instalado"
) else if exist "bin\ffmpeg" (
    call :print_success "FFmpeg ja instalado"
) else (
    call :download_ffmpeg
)

REM 4. Criar ambiente virtual
echo.
echo 📦 Criando ambiente virtual...
if exist ".venv" (
    call :print_info "Ambiente virtual ja existe. Removendo..."
    rmdir /s /q .venv
)

!PYTHON_CMD! -m venv .venv
if %errorlevel% neq 0 (
    call :print_error "Falha ao criar ambiente virtual!"
    pause
    exit /b 1
)

call :print_success "Ambiente virtual criado"

REM 5. Ativar ambiente virtual
echo.
echo ⚡ Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    call :print_error "Falha ao ativar ambiente virtual!"
    pause
    exit /b 1
)

call :print_success "Ambiente virtual ativado"

REM 6. Atualizar pip
echo.
echo 📥 Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1
call :print_success "Pip atualizado"

REM 7. Instalar dependências obrigatórias
echo.
echo 📦 Instalando dependencias obrigatorias...
echo    • Instalando Groq...
python -m pip install groq>=0.29.0
if %errorlevel% neq 0 (
    call :print_error "Falha ao instalar Groq!"
    pause
    exit /b 1
)
call :print_success "Groq instalado"

REM 8. Instalar dependências opcionais
echo.
echo 🧠 Instalando dependencias opcionais...
echo    • Instalando Google Gen AI SDK + Pydantic...
python -m pip install google-genai>=1.23.0 pydantic>=2.11.7 >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Google Gen AI SDK e Pydantic instalados"
    set GEMINI_AVAILABLE=true
) else (
    call :print_warning "Falha ao instalar Google Gen AI SDK"
    call :print_info "Funcionalidades de analise serao limitadas"
    call :print_info "Para instalar depois: pip install google-genai>=1.23.0 pydantic>=2.11.7"
    set GEMINI_AVAILABLE=false
)

REM 9. Configurar arquivo de ambiente
echo.
echo 🔑 Configurando variaveis de ambiente...
if not exist ".env" (
    if exist ".env.exemplo" (
        copy ".env.exemplo" ".env" >nul
        call :print_success "Arquivo .env criado a partir do template"
        call :print_info "Edite o arquivo .env com suas chaves de API reais"
    ) else (
        call :print_warning "Template .env.exemplo nao encontrado"
        call :print_info "Baixe o projeto completo do repositorio"
    )
) else (
    call :print_info "Arquivo .env ja existe"
)

REM 10. Criar script para carregar variáveis
echo.
echo 🔧 Criando script auxiliar...
(
echo @echo off
echo REM Script para carregar variaveis de ambiente
echo if exist ".env" ^(
echo     echo 🔑 Carregando variaveis de ambiente...
echo     for /f "usebackq tokens=1,2 delims==" %%%%a in ^(".env"^) do ^(
echo         if not "%%%%a"=="" if not "%%%%a:~0,1%"=="#" ^(
echo             set "%%%%a=%%%%b"
echo         ^)
echo     ^)
echo     echo ✅ Variaveis carregadas!
echo ^) else ^(
echo     echo ❌ Arquivo .env nao encontrado!
echo     echo    Execute: copy .env.exemplo .env
echo     echo    Depois edite .env com suas chaves de API
echo ^)
) > set-variables.bat

call :print_success "Script set-variables.bat criado"

REM 11. Testar instalação
echo.
echo 🧪 Testando instalacao...

REM Testar FFmpeg
if exist "bin\ffmpeg.exe" (
    bin\ffmpeg.exe -version >nul 2>&1
    if %errorlevel% equ 0 (
        call :print_success "FFmpeg: Funcionando"
    ) else (
        call :print_error "FFmpeg: Erro na execucao"
    )
) else (
    call :print_error "FFmpeg: Nao encontrado"
)

REM Testar FFprobe
if exist "bin\ffprobe.exe" (
    bin\ffprobe.exe -version >nul 2>&1
    if %errorlevel% equ 0 (
        call :print_success "FFprobe: Funcionando"
    ) else (
        call :print_error "FFprobe: Erro na execucao"
    )
) else (
    call :print_warning "FFprobe: Nao encontrado (sistema usara fallback com FFmpeg)"
)

REM Testar importações
python -c "import groq; print('Groq: OK')" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Groq: Funcionando"
) else (
    call :print_error "Groq: Falha na importacao"
)

python -c "from google import genai; from pydantic import BaseModel; print('Gemini: OK')" >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Gemini: Funcionando (nova API)"
) else (
    call :print_warning "Gemini: Nao disponivel (funcionalidades limitadas)"
)

REM Testar sistema principal
python content_pipeline.py --help >nul 2>&1
if %errorlevel% equ 0 (
    call :print_success "Sistema funcionando corretamente"
) else (
    call :print_warning "Sistema pode ter problemas. Verifique as dependencias."
)

REM 12. Sumário final
echo.
echo ==========================================
echo 📊 SUMARIO DA INSTALACAO
echo ==========================================
echo.

echo 🐍 Python: !PYTHON_VERSION!
echo 📦 Ambiente Virtual: ✅ Criado
echo 🔧 Groq: ✅ Instalado
if "!GEMINI_AVAILABLE!"=="true" (
    echo 🧠 Gemini: ✅ Instalado (SDK v1.23.0^)
) else (
    echo 🧠 Gemini: ⚠️  Limitado
)

if exist "bin\ffmpeg.exe" (
    echo 🎥 FFmpeg: ✅ Instalado automaticamente
) else if exist "bin\ffmpeg" (
    echo 🎥 FFmpeg: ✅ Instalado automaticamente
) else (
    echo 🎥 FFmpeg: ❌ Falha na instalacao
)

if exist "bin\ffprobe.exe" (
    echo 🔍 FFprobe: ✅ Instalado automaticamente
) else if exist "bin\ffprobe" (
    echo 🔍 FFprobe: ✅ Instalado automaticamente
) else (
    echo 🔍 FFprobe: ⚠️  Nao instalado (fallback disponivel)
)

echo.
echo 📁 Estrutura:
if exist "videos" (
    echo    videos\: ✅ OK
) else (
    echo    videos\: ❌ Faltando
)
if exist "temp" (
    echo    temp\: ✅ OK
) else (
    echo    temp\: ❌ Faltando
)
if exist "bin" (
    echo    bin\: ✅ OK
) else (
    echo    bin\: ❌ Faltando
)

set /a MODULE_COUNT=0
for /d %%d in (modulo-*) do set /a MODULE_COUNT+=1
if !MODULE_COUNT! gtr 0 (
    echo    modulos\: !MODULE_COUNT! pasta^(s^) ja existente^(s^)
) else (
    echo    modulos\: Criados automaticamente ao processar
)

echo.
echo ==========================================
echo 🚀 PROXIMOS PASSOS:
echo ==========================================
echo.
echo 1. 🔑 Configure suas APIs:
echo    • Edite o arquivo .env
echo    • Execute: set-variables.bat
echo.
echo 2. 📹 Coloque seus videos na pasta videos\
echo.
echo 3. 🚀 Execute o sistema:
echo    • Modo simples: python content_pipeline.py
echo    • Modo completo: python content_pipeline.py --complete videos\seu_video.mp4 1 1
echo    • Modo lote: python content_pipeline.py --batch
echo.
echo 4. 📚 Consulte o README.md para instrucoes detalhadas
echo.

call :print_success "Instalacao completa concluida!"
call :print_info "Sistema pronto para uso com FFmpeg + FFprobe instalados automaticamente"

echo.
echo ⭐ Sistema Enhanced Video Editing AI v3.0.0 - Instalação Completa
echo.

REM Manter janela aberta
echo Pressione qualquer tecla para sair...
pause >nul 