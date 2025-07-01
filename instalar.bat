@echo off
setlocal enabledelayedexpansion

REM ===============================================
REM  🤖 Sistema de Transcrição Inteligente
REM  Instalador Automático para Windows
REM  Versão: 2.0.0 - Full Stack Club
REM ===============================================

echo.
echo ==========================================
echo 🤖 Sistema de Transcricao Inteligente
echo    Instalador para Windows
echo ==========================================
echo.

REM Verificar se estamos no diretório correto
if not exist "transcribe.py" (
    echo ❌ ERRO: transcribe.py nao encontrado!
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

REM 2. Criar ambiente virtual
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

REM 3. Ativar ambiente virtual
echo.
echo ⚡ Ativando ambiente virtual...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    call :print_error "Falha ao ativar ambiente virtual!"
    pause
    exit /b 1
)

call :print_success "Ambiente virtual ativado"

REM 4. Atualizar pip
echo.
echo 📥 Atualizando pip...
python -m pip install --upgrade pip >nul 2>&1
call :print_success "Pip atualizado"

REM 5. Instalar dependências obrigatórias
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

REM 6. Instalar dependências opcionais
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

REM 7. Criar estrutura de diretórios
echo.
echo 📁 Criando estrutura de diretorios...
if not exist "videos" mkdir videos
if not exist "temp" mkdir temp

call :print_success "Diretorios criados: videos\, temp\"
call :print_info "Modulos serao criados automaticamente ao processar videos"

REM 8. Verificar FFmpeg
echo.
echo 🎥 Verificando FFmpeg...
if exist "bin\ffmpeg.exe" (
    call :print_success "FFmpeg encontrado no projeto"
) else if exist "bin\ffmpeg" (
    call :print_success "FFmpeg encontrado no projeto"
) else (
    call :print_warning "FFmpeg nao encontrado em bin\"
    call :print_info "Sistema pode nao funcionar sem FFmpeg"
    call :print_info "Baixe em: https://ffmpeg.org/download.html"
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
python transcribe.py >nul 2>&1
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
    echo 🎥 FFmpeg: ✅ Incluido no projeto
) else if exist "bin\ffmpeg" (
    echo 🎥 FFmpeg: ✅ Incluido no projeto
) else (
    echo 🎥 FFmpeg: ⚠️  Nao encontrado
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
echo    • Modo simples: python transcribe.py videos\seu_video.mp4
echo    • Modo completo: python transcribe.py --complete videos\seu_video.mp4 1 1
echo    • Modo lote: python transcribe.py --batch
echo.
echo 4. 📚 Consulte o guia: type PROJETO_TRANSCRICAO_AULAS.md
echo.

call :print_success "Instalacao concluida!"
call :print_info "Leia o PROJETO_TRANSCRICAO_AULAS.md para instrucoes detalhadas"

echo.
echo ⭐ Sistema Enhanced Transcription v2.0.0 - Full Stack Club
echo.

REM Manter janela aberta
echo Pressione qualquer tecla para sair...
pause >nul 