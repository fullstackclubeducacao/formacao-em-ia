#!/bin/bash
# ===============================================
# 🤖 Sistema de Transcrição Inteligente
# Instalador Automático para Mac/Linux
# Versão: 2.0.0 - Full Stack Club
# ===============================================

set -e  # Parar em caso de erro

echo ""
echo "=========================================="
echo "🤖 Sistema de Transcrição Inteligente"
echo "   Instalador para Mac/Linux"
echo "=========================================="
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "transcribe.py" ]; then
    echo "❌ ERRO: transcribe.py não encontrado!"
    echo "   Execute este instalador na pasta raiz do projeto."
    exit 1
fi

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para prints coloridos
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 1. Verificar Python
echo "🐍 Verificando Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_status "Python encontrado: $PYTHON_VERSION"
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    if [ "$PYTHON_MAJOR" -eq 3 ]; then
        print_status "Python encontrado: $PYTHON_VERSION"
        PYTHON_CMD="python"
    else
        print_error "Python 3.8+ necessário. Encontrado Python $PYTHON_VERSION"
        echo ""
        echo "📥 Instale Python 3.8+ usando:"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "   brew install python3"
            echo "   ou baixe em: https://www.python.org/downloads/"
        else
            echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
            echo "   ou sudo yum install python3 python3-pip"
        fi
        exit 1
    fi
else
    print_error "Python não encontrado!"
    echo ""
    echo "📥 Instale Python 3.8+ usando:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   brew install python3"
        echo "   ou baixe em: https://www.python.org/downloads/"
    else
        echo "   sudo apt update && sudo apt install python3 python3-pip python3-venv"
        echo "   ou sudo yum install python3 python3-pip"
    fi
    exit 1
fi

# 2. Verificar versão do Python
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8+ é necessário. Versão atual: $PYTHON_VERSION"
    exit 1
fi

# 3. Verificar pip
echo ""
echo "📦 Verificando pip..."
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    print_error "pip não encontrado!"
    echo ""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   Instale com: python3 -m ensurepip --upgrade"
    else
        echo "   sudo apt install python3-pip"
        echo "   ou sudo yum install python3-pip"
    fi
    exit 1
fi

print_status "pip disponível"

# 4. Criar ambiente virtual
echo ""
echo "📦 Criando ambiente virtual..."
if [ -d ".venv" ]; then
    print_info "Ambiente virtual já existe. Removendo..."
    rm -rf .venv
fi

$PYTHON_CMD -m venv .venv
if [ $? -ne 0 ]; then
    print_error "Falha ao criar ambiente virtual!"
    print_info "Instale python3-venv: sudo apt install python3-venv"
    exit 1
fi

print_status "Ambiente virtual criado"

# 5. Ativar ambiente virtual
echo ""
echo "⚡ Ativando ambiente virtual..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    print_error "Falha ao ativar ambiente virtual!"
    exit 1
fi

print_status "Ambiente virtual ativado"

# 6. Atualizar pip
echo ""
echo "📥 Atualizando pip..."
python -m pip install --upgrade pip >/dev/null 2>&1
print_status "Pip atualizado"

# 7. Instalar dependências obrigatórias
echo ""
echo "📦 Instalando dependências obrigatórias..."
echo "   • Instalando Groq..."
python -m pip install groq>=0.29.0
if [ $? -ne 0 ]; then
    print_error "Falha ao instalar Groq!"
    exit 1
fi
print_status "Groq instalado"

# 8. Instalar dependências opcionais
echo ""
echo "🧠 Instalando dependências opcionais..."
echo "   • Instalando Google Gen AI SDK + Pydantic..."
if python -m pip install google-genai>=1.23.0 pydantic>=2.11.7 >/dev/null 2>&1; then
    print_status "Google Gen AI SDK e Pydantic instalados"
    GEMINI_AVAILABLE=true
else
    print_warning "Falha ao instalar Google Gen AI SDK"
    print_info "Funcionalidades de análise serão limitadas"
    print_info "Para instalar depois: pip install google-genai>=1.23.0 pydantic>=2.11.7"
    GEMINI_AVAILABLE=false
fi

# 9. Criar estrutura de diretórios
echo ""
echo "📁 Criando estrutura de diretórios..."
mkdir -p videos temp

print_status "Diretórios criados: videos/, temp/"
print_info "Módulos serão criados automaticamente ao processar vídeos"

# 10. Verificar e dar permissões ao FFmpeg
echo ""
echo "🎥 Verificando FFmpeg..."
if [ -f "./bin/ffmpeg" ] && [ -f "./bin/ffprobe" ]; then
    chmod +x ./bin/ffmpeg ./bin/ffprobe
    if [ -x "./bin/ffmpeg" ]; then
        FFMPEG_VERSION=$(./bin/ffmpeg -version 2>/dev/null | head -n1 | cut -d' ' -f3)
        print_status "FFmpeg configurado: $FFMPEG_VERSION"
        FFMPEG_AVAILABLE=true
    else
        print_warning "FFmpeg existe mas não tem permissões de execução"
        FFMPEG_AVAILABLE=false
    fi
else
    print_warning "FFmpeg não encontrado em ./bin/"
    print_info "Sistema pode não funcionar sem FFmpeg"
    print_info "Baixe em: https://ffmpeg.org/download.html"
    FFMPEG_AVAILABLE=false
fi

# 11. Configurar arquivo de ambiente
echo ""
echo "🔑 Configurando variáveis de ambiente..."
if [ ! -f ".env" ]; then
    if [ -f ".env.exemplo" ]; then
        cp .env.exemplo .env
        print_status "Arquivo .env criado a partir do template"
        print_info "Edite o arquivo .env com suas chaves de API reais"
    else
        print_warning "Template .env.exemplo não encontrado"
        print_info "Baixe o projeto completo do repositório"
    fi
else
    print_info "Arquivo .env já existe"
fi

# 12. Dar permissões aos scripts
echo ""
echo "🔧 Configurando permissões..."
chmod +x transcribe.py
chmod +x instalar.sh
if [ -f "setup.sh" ]; then
    chmod +x setup.sh
fi
print_status "Permissões configuradas"

# 13. Testar instalação
echo ""
echo "🧪 Testando instalação..."

# Testar importações
if python -c "import groq; print('Groq: OK')" >/dev/null 2>&1; then
    print_status "Groq: Funcionando"
else
    print_error "Groq: Falha na importação"
fi

if python -c "from google import genai; from pydantic import BaseModel; print('Gemini: OK')" >/dev/null 2>&1; then
    print_status "Gemini: Funcionando (nova API)"
else
    print_warning "Gemini: Não disponível (funcionalidades limitadas)"
fi

# Testar sistema principal
if python transcribe.py >/dev/null 2>&1; then
    print_status "Sistema funcionando corretamente"
else
    print_warning "Sistema pode ter problemas. Verifique as dependências."
fi

# 14. Sumário final
echo ""
echo "=========================================="
echo "📊 SUMÁRIO DA INSTALAÇÃO"
echo "=========================================="
echo ""

# Detectar sistema operacional
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_NAME="macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_NAME="Linux"
else
    OS_NAME="Unix"
fi

echo "💻 Sistema: $OS_NAME"
echo "🐍 Python: $PYTHON_VERSION"
echo "📦 Ambiente Virtual: ✅ Criado"
echo "🔧 Groq: $([ "$(python -c "import groq" 2>/dev/null; echo $?)" -eq 0 ] && echo "✅ OK" || echo "❌ Falha")"
echo "🧠 Gemini: $([ "$(python -c "from google import genai; from pydantic import BaseModel" 2>/dev/null; echo $?)" -eq 0 ] && echo "✅ OK (SDK v1.23.0)" || echo "⚠️  Limitado")"
echo "🎥 FFmpeg: $([ "$FFMPEG_AVAILABLE" = true ] && echo "✅ OK" || echo "⚠️  Não encontrado")"

echo ""
echo "📁 Estrutura:"
echo "   videos/: $([ -d "videos" ] && echo "✅ OK" || echo "❌ Faltando")"
echo "   temp/: $([ -d "temp" ] && echo "✅ OK" || echo "❌ Faltando")"
EXISTING_MODULES=$(ls -1d modulo-*/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$EXISTING_MODULES" -gt 0 ]; then
    echo "   modulos/: $EXISTING_MODULES pasta(s) já existente(s)"
else
    echo "   modulos/: Criados automaticamente ao processar"
fi

echo ""
echo "=========================================="
echo "🚀 PRÓXIMOS PASSOS:"
echo "=========================================="
echo ""

# Verificar o que ainda precisa ser feito
NEEDS_GROQ_API=$([ -z "$GROQ_API_KEY" ] && echo "sim" || echo "não")
NEEDS_GEMINI_API=$([ -z "$GEMINI_API_KEY" ] && echo "sim" || echo "não")

if [ "$NEEDS_GROQ_API" = "sim" ]; then
    echo "1. 🔑 Configure sua API Groq:"
    echo "   • Obtenha em: https://console.groq.com/"
    echo "   • Edite o arquivo .env"
    echo "   • Execute: source .env"
    echo ""
fi

if [ "$NEEDS_GEMINI_API" = "sim" ]; then
    echo "2. 🧠 Configure sua API Gemini (opcional):"
    echo "   • Obtenha em: https://ai.google.dev/"
    echo "   • Edite o arquivo .env"
    echo "   • Execute: source .env"
    echo ""
fi

echo "3. 📹 Coloque seus vídeos na pasta videos/"
echo ""

echo "4. 🚀 Execute o sistema:"
echo "   # Ativar ambiente virtual"
echo "   source .venv/bin/activate"
echo ""
echo "   # Carregar variáveis"
echo "   source .env"
echo ""
echo "   # Modos de uso"
echo "   python transcribe.py videos/seu_video.mp4              # Simples"
echo "   python transcribe.py --complete videos/seu_video.mp4 1 1  # Completo"
echo "   python transcribe.py --batch                          # Lote"
echo ""

echo "5. 📚 Consulte o guia completo:"
echo "   cat PROJETO_TRANSCRICAO_AULAS.md"
echo ""

print_status "Instalação concluída!"
print_info "Leia o PROJETO_TRANSCRICAO_AULAS.md para instruções detalhadas"

echo ""
echo "⭐ Sistema Enhanced Transcription v2.0.0 - Full Stack Club"
echo ""

# Criar arquivos auxiliares do sistema
echo ""
echo "🔧 Criando scripts de facilitação..."

# 1. Criar .env.exemplo se não existir
if [ ! -f ".env.exemplo" ]; then
    cat > .env.exemplo << 'EOF'
# ===============================================
# 🤖 Sistema de Transcrição Inteligente
# Configurações de Ambiente
# ===============================================

# --- APIs OBRIGATÓRIAS ---
# Obtenha sua chave em: https://console.groq.com/
GROQ_API_KEY=sua_chave_groq_aqui

# --- APIs OPCIONAIS ---
# Para análise inteligente - Obtenha em: https://ai.google.dev/
GEMINI_API_KEY=sua_chave_gemini_aqui

# --- CONFIGURAÇÕES DE TRANSCRIÇÃO ---
# Tamanho dos chunks em segundos (padrão: 600 = 10 minutos)
CHUNK_SIZE_SECONDS=600

# Modelo Groq para transcrição (opções: whisper-large-v3-turbo, whisper-large-v3)
GROQ_MODEL=whisper-large-v3-turbo

# Idioma da transcrição (pt, en, es, fr, etc)
GROQ_LANGUAGE=pt

# --- CONFIGURAÇÕES DE SISTEMA ---
# Timeout para requisições em segundos
REQUEST_TIMEOUT=300

# Número máximo de tentativas em caso de erro
MAX_RETRIES=3

# Modo debug (true/false)
DEBUG_MODE=false

# Salvar arquivos de debug (true/false)
SAVE_DEBUG_FILES=false

# --- CONFIGURAÇÕES DE GEMINI ---
# Modelo Gemini para análise (gemini-2.5-flash, gemini-2.5-pro)
GEMINI_MODEL=gemini-2.5-flash

# Habilitar thinking do Gemini (true/false)
GEMINI_THINKING=true

# Budget de thinking (-1 = dinâmico)
GEMINI_THINKING_BUDGET=-1

# Contexto máximo em tokens
GEMINI_MAX_CONTEXT=1000000

# --- CAMINHOS DO SISTEMA ---
# Caminho para o FFmpeg (deixe como está se usar o fornecido)
FFMPEG_PATH=./bin/ffmpeg
FFPROBE_PATH=./bin/ffprobe

# Diretórios
TEMP_DIR_NAME=temp
OUTPUT_BASE_DIR=modulo-{modulo:02d}
VIDEOS_DIR=videos

# --- CONFIGURAÇÕES DE ÁUDIO ---
# Taxa de amostragem do áudio
AUDIO_SAMPLE_RATE=16000

# Número de canais de áudio
AUDIO_CHANNELS=1

# Formato de áudio para processamento
AUDIO_FORMAT=flac

# --- CONFIGURAÇÕES DE ORGANIZAÇÃO ---
# Padrão do nome das pastas de aula
AULA_DIR_PATTERN=aula-{numero:02d}-{slug}

# ===============================================
# 📋 INSTRUÇÕES:
# ===============================================
# 1. Copie este arquivo para .env
# 2. Substitua "sua_chave_groq_aqui" pela sua chave real do Groq
# 3. Opcionalmente, adicione a chave do Gemini para análise inteligente
# 4. Execute: source .env (ou use o script ativar.sh)
# 5. As outras configurações podem ficar com os valores padrão
# ===============================================
EOF
    print_status "Arquivo .env.exemplo criado"
fi

# 2. Criar script de ativação rápida
cat > ativar.sh << 'EOF'
#!/bin/bash
# Script de ativação rápida do Sistema de Transcrição

echo "🤖 Sistema de Transcrição Inteligente"
echo "======================================"

# Ativar ambiente virtual
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Ambiente virtual ativado"
else
    echo "❌ Ambiente virtual não encontrado. Execute: ./instalar.sh"
    exit 1
fi

# Carregar variáveis de ambiente
if [ -f ".env" ]; then
    source .env
    echo "✅ Variáveis de ambiente carregadas"
else
    echo "⚠️  Arquivo .env não encontrado"
    echo "   Execute: cp .env.exemplo .env"
    echo "   Depois edite .env com suas chaves de API"
fi

echo ""
echo "🚀 Sistema pronto! Comandos disponíveis:"
echo "   python transcribe.py videos/video.mp4         # Simples"
echo "   python transcribe.py --complete video.mp4 1 1 # Completo"
echo "   python transcribe.py --batch                  # Lote"
echo ""
EOF

# 3. Criar script de execução automática (run.sh)
cat > run.sh << 'EOF'
#!/bin/bash
# ===============================================
# 🤖 Script de Execução Automática
# Sistema de Transcrição Inteligente
# ===============================================

set -e

# Função para prints coloridos
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

echo "🤖 Sistema de Transcrição Inteligente - Execução Automática"
echo "============================================================="

# 1. Verificar se estamos no diretório correto
if [ ! -f "transcribe.py" ]; then
    print_error "transcribe.py não encontrado!"
    echo "Execute este script na pasta raiz do projeto."
    exit 1
fi

# 2. Verificar e ativar ambiente virtual
if [ ! -d ".venv" ]; then
    print_error "Ambiente virtual não encontrado!"
    echo "Execute primeiro: ./instalar.sh"
    exit 1
fi

print_info "Ativando ambiente virtual..."
source .venv/bin/activate
print_status "Ambiente virtual ativado"

# 3. Carregar variáveis de ambiente
if [ -f ".env" ]; then
    source .env
    print_status "Variáveis de ambiente carregadas"
else
    print_warning "Arquivo .env não encontrado"
    if [ -f ".env.exemplo" ]; then
        print_info "Copiando .env.exemplo para .env..."
        cp .env.exemplo .env
        print_warning "⚠️  ATENÇÃO: Configure suas chaves de API no arquivo .env"
        print_info "Edite o arquivo .env e adicione suas chaves:"
        print_info "  • GROQ_API_KEY=sua_chave_aqui"
        print_info "  • GEMINI_API_KEY=sua_chave_aqui (opcional)"
        echo ""
        read -p "Pressione Enter após configurar o .env ou Ctrl+C para cancelar..."
        source .env
    else
        print_error "Nem .env nem .env.exemplo encontrados"
        exit 1
    fi
fi

# 4. Verificar se as chaves essenciais estão configuradas
if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "sua_chave_groq_aqui" ]; then
    print_error "GROQ_API_KEY não configurada corretamente no .env"
    print_info "1. Obtenha sua chave em: https://console.groq.com/"
    print_info "2. Edite o arquivo .env"
    print_info "3. Substitua 'sua_chave_groq_aqui' pela sua chave real"
    exit 1
fi

# 5. Verificar se o Python e dependências estão OK
if ! python -c "import groq" >/dev/null 2>&1; then
    print_error "Groq não está instalado corretamente"
    print_info "Execute: ./instalar.sh"
    exit 1
fi

print_status "Sistema verificado e pronto!"

# 6. Executar o comando Python
if [ $# -eq 0 ]; then
    # Sem argumentos - mostrar ajuda
    echo ""
    print_info "Executando python transcribe.py (modo ajuda)..."
    python transcribe.py
else
    # Com argumentos - executar comando
    echo ""
    print_info "Executando: python transcribe.py $*"
    echo ""
    python transcribe.py "$@"
fi

echo ""
print_status "Execução concluída!"
EOF

# 4. Criar script interativo completo
cat > interactive.sh << 'EOF'
#!/bin/bash
# ===============================================
# 🤖 Script Interativo
# Sistema de Transcrição Inteligente
# ===============================================

set -e

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

print_title() { echo -e "${PURPLE}🤖 $1${NC}"; }
print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_question() { echo -e "${CYAN}❓ $1${NC}"; }

clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🤖 Sistema de Transcrição Inteligente - Modo Interativo    ║"
echo "║  🎯 Vamos configurar e executar tudo passo a passo!         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Função para mostrar loading
show_loading() {
    local duration=$1
    local message=$2
    echo -n "$message"
    for i in $(seq 1 $duration); do
        echo -n "."
        sleep 0.5
    done
    echo " Pronto!"
}

# 1. Verificações iniciais
print_title "ETAPA 1: Verificações do Sistema"
echo "────────────────────────────────────────"

if [ ! -f "transcribe.py" ]; then
    print_error "Sistema não encontrado neste diretório!"
    echo "Execute este script na pasta raiz do projeto."
    exit 1
fi

if [ ! -d ".venv" ]; then
    print_error "Ambiente virtual não encontrado!"
    echo ""
    read -p "Deseja executar a instalação agora? (s/n): " install_choice
    if [[ $install_choice =~ ^[Ss]$ ]]; then
        print_info "Executando instalação..."
        ./instalar.sh
        echo ""
        print_status "Instalação concluída! Continue..."
        read -p "Pressione Enter para continuar..."
    else
        print_info "Execute primeiro: ./instalar.sh"
        exit 1
    fi
fi

print_status "Sistema encontrado e verificado"

# 2. Ativar ambiente
print_info "Ativando ambiente virtual..."
source .venv/bin/activate
print_status "Ambiente ativado"

# 3. Configurar .env
print_title "ETAPA 2: Configuração das APIs"
echo "────────────────────────────────────────"

if [ ! -f ".env" ]; then
    if [ -f ".env.exemplo" ]; then
        print_info "Criando arquivo .env a partir do template..."
        cp .env.exemplo .env
        print_status "Arquivo .env criado"
    else
        print_error "Template .env.exemplo não encontrado"
        exit 1
    fi
fi

source .env

# Verificar GROQ_API_KEY
if [ -z "$GROQ_API_KEY" ] || [ "$GROQ_API_KEY" = "sua_chave_groq_aqui" ]; then
    echo ""
    print_warning "Chave da API Groq não configurada"
    echo ""
    echo "📋 Para obter sua chave Groq:"
    echo "   1. Acesse: https://console.groq.com/"
    echo "   2. Faça login ou crie uma conta"
    echo "   3. Gere uma nova API Key"
    echo "   4. Copie a chave gerada"
    echo ""
    
    while true; do
        print_question "Você já tem uma chave da API Groq? (s/n)"
        read -r groq_choice
        
        if [[ $groq_choice =~ ^[Ss]$ ]]; then
            print_question "Cole sua chave da API Groq:"
            read -r groq_key
            if [ ! -z "$groq_key" ] && [ "$groq_key" != "sua_chave_groq_aqui" ]; then
                # Substituir no .env
                if command -v sed >/dev/null 2>&1; then
                    sed -i.backup "s/GROQ_API_KEY=.*/GROQ_API_KEY=$groq_key/" .env
                    print_status "Chave Groq configurada com sucesso!"
                    export GROQ_API_KEY="$groq_key"
                    break
                else
                    print_warning "Edite manualmente o arquivo .env com sua chave"
                    break
                fi
            else
                print_error "Chave inválida. Tente novamente."
            fi
        elif [[ $groq_choice =~ ^[Nn]$ ]]; then
            print_info "Obtenha sua chave em: https://console.groq.com/"
            print_warning "O sistema não funcionará sem a chave Groq"
            exit 1
        else
            print_warning "Resposta inválida. Digite 's' para sim ou 'n' para não."
        fi
    done
else
    print_status "Chave Groq já configurada"
fi

# Verificar GEMINI_API_KEY (opcional)
if [ -z "$GEMINI_API_KEY" ] || [ "$GEMINI_API_KEY" = "sua_chave_gemini_aqui" ]; then
    echo ""
    print_question "Deseja configurar a API do Gemini para análise inteligente? (s/n)"
    echo "   (Opcional - sem ela o sistema funciona com análise básica)"
    
    read -r gemini_choice
    if [[ $gemini_choice =~ ^[Ss]$ ]]; then
        echo ""
        echo "📋 Para obter sua chave Gemini:"
        echo "   1. Acesse: https://ai.google.dev/"
        echo "   2. Clique em 'Get API Key'"
        echo "   3. Faça login com conta Google"
        echo "   4. Crie uma nova API Key"
        echo ""
        
        print_question "Cole sua chave da API Gemini:"
        read -r gemini_key
        if [ ! -z "$gemini_key" ] && [ "$gemini_key" != "sua_chave_gemini_aqui" ]; then
            if command -v sed >/dev/null 2>&1; then
                sed -i.backup "s/GEMINI_API_KEY=.*/GEMINI_API_KEY=$gemini_key/" .env
                print_status "Chave Gemini configurada!"
                export GEMINI_API_KEY="$gemini_key"
            fi
        fi
    else
        print_info "Continuando sem Gemini - análise básica será usada"
    fi
else
    print_status "Chave Gemini já configurada"
fi

# Recarregar .env
source .env

# 4. Listar vídeos disponíveis
print_title "ETAPA 3: Seleção de Vídeos"
echo "────────────────────────────────────────"

if [ ! -d "videos" ]; then
    mkdir -p videos
    print_info "Pasta 'videos' criada"
fi

# Encontrar vídeos (máxima compatibilidade com espaços nos nomes)
video_files=()
if command -v find >/dev/null 2>&1; then
    # Usar método mais compatível para shells diferentes
    OLD_IFS="$IFS"
    IFS=$'\n'
    for file in $(find videos -type f \( -name "*.mp4" -o -name "*.avi" -o -name "*.mov" -o -name "*.mkv" -o -name "*.webm" -o -name "*.m4v" \) 2>/dev/null | sort); do
        if [ -f "$file" ]; then
            video_files+=("$file")
        fi
    done
    IFS="$OLD_IFS"
fi

if [ ${#video_files[@]} -eq 0 ]; then
    print_warning "Nenhum vídeo encontrado na pasta 'videos'"
    echo ""
    print_info "Coloque seus vídeos na pasta 'videos' e execute novamente"
    print_info "Formatos suportados: mp4, avi, mov, mkv, webm, m4v"
    echo ""
    read -p "Pressione Enter para abrir a pasta 'videos'..."
    
    # Tentar abrir a pasta
    if command -v open >/dev/null 2>&1; then
        open videos  # macOS
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open videos  # Linux
    fi
    
    exit 0
fi

echo ""
print_status "Vídeos encontrados:"
for i in "${!video_files[@]}"; do
    video_path="${video_files[$i]}"
    filename=$(basename "$video_path")
    # Calcular tamanho do arquivo de forma segura
    if [ -f "$video_path" ]; then
        filesize=$(du -h "$video_path" 2>/dev/null | cut -f1)
        [ -z "$filesize" ] && filesize="?"
    else
        filesize="?"
    fi
    echo "   $((i+1)). $filename ($filesize)"
done

# 5. Escolher modo de processamento
echo ""
print_title "ETAPA 4: Modo de Processamento"
echo "────────────────────────────────────────"
echo ""
echo "Escolha o modo de processamento:"
echo ""
echo "   1. 🎯 INDIVIDUAL - Processar um vídeo específico (recomendado)"
echo "   2. 📚 LOTE - Processar todos os vídeos automaticamente"
echo "   3. 🔧 SIMPLES - Apenas transcrever (modo original)"
echo ""

while true; do
    print_question "Digite sua escolha (1, 2 ou 3):"
    read -r mode_choice
    
    case $mode_choice in
        1)
            # Modo individual
            echo ""
            print_info "Modo Individual Selecionado"
            echo ""
            print_question "Qual vídeo deseja processar? (digite o número)"
            
            while true; do
                read -r video_choice
                if [[ $video_choice =~ ^[0-9]+$ ]] && [ $video_choice -ge 1 ] && [ $video_choice -le ${#video_files[@]} ]; then
                    selected_video="${video_files[$((video_choice-1))]}"
                    print_status "Vídeo selecionado: $(basename "$selected_video")"
                    break
                else
                    print_error "Número inválido. Digite um número entre 1 e ${#video_files[@]}"
                fi
            done
            
            # Perguntar módulo e aula
            echo ""
            print_question "Em qual módulo está esta aula? (digite o número, ex: 1)"
            read -r modulo_num
            modulo_num=${modulo_num:-1}
            
            print_question "Qual é o número desta aula? (digite o número, ex: 1)"
            read -r aula_num
            aula_num=${aula_num:-1}
            
            # Confirmação
            echo ""
            print_info "Configuração escolhida:"
            echo "   📹 Vídeo: $(basename "$selected_video")"
            echo "   📚 Módulo: $modulo_num"
            echo "   📖 Aula: $aula_num"
            echo "   🔄 Modo: Processamento Completo (transcrição + análise + documentação)"
            echo ""
            
            print_question "Confirma o processamento? (s/n)"
            read -r confirm
            if [[ $confirm =~ ^[Ss]$ ]]; then
                echo ""
                print_title "INICIANDO PROCESSAMENTO..."
                echo "────────────────────────────────────────"
                
                show_loading 3 "🚀 Preparando sistema"
                
                # Executar processamento
                python transcribe.py --complete "$selected_video" "$modulo_num" "$aula_num"
                
                echo ""
                print_status "🎉 Processamento concluído com sucesso!"
                echo ""
                print_info "📁 Verifique a pasta criada em: modulo-$(printf "%02d" $modulo_num)/"
                print_info "📄 Arquivos gerados:"
                echo "   • README.md (documentação completa)"
                echo "   • transcricao.json (texto transcrito)"
                echo "   • analise.json (análise estruturada)"
                echo "   • scripts/ (comandos extraídos)"
            else
                print_info "Processamento cancelado"
            fi
            break
            ;;
        2)
            # Modo lote
            echo ""
            print_info "Modo Lote Selecionado"
            echo ""
            print_question "A partir de qual módulo iniciar? (ex: 1)"
            read -r start_modulo
            start_modulo=${start_modulo:-1}
            
            # Confirmação
            echo ""
            print_info "Configuração escolhida:"
            echo "   📹 Vídeos: ${#video_files[@]} arquivos"
            echo "   📚 Módulo inicial: $start_modulo"
            echo "   🔄 Modo: Processamento em Lote"
            echo ""
            
            print_question "Confirma o processamento de TODOS os vídeos? (s/n)"
            read -r confirm
            if [[ $confirm =~ ^[Ss]$ ]]; then
                echo ""
                print_title "INICIANDO PROCESSAMENTO EM LOTE..."
                echo "────────────────────────────────────────"
                
                show_loading 3 "🚀 Preparando sistema para lote"
                
                # Executar processamento em lote
                python transcribe.py --batch videos "$start_modulo"
                
                echo ""
                print_status "🎉 Processamento em lote concluído!"
            else
                print_info "Processamento cancelado"
            fi
            break
            ;;
        3)
            # Modo simples
            echo ""
            print_info "Modo Simples Selecionado (apenas transcrição)"
            echo ""
            print_question "Qual vídeo deseja processar? (digite o número)"
            
            while true; do
                read -r video_choice
                if [[ $video_choice =~ ^[0-9]+$ ]] && [ $video_choice -ge 1 ] && [ $video_choice -le ${#video_files[@]} ]; then
                    selected_video="${video_files[$((video_choice-1))]}"
                    print_status "Vídeo selecionado: $(basename "$selected_video")"
                    break
                else
                    print_error "Número inválido. Digite um número entre 1 e ${#video_files[@]}"
                fi
            done
            
            # Confirmação
            echo ""
            print_info "Configuração escolhida:"
            echo "   📹 Vídeo: $(basename "$selected_video")"
            echo "   🔄 Modo: Transcrição Simples (sem análise)"
            echo ""
            
            print_question "Confirma o processamento? (s/n)"
            read -r confirm
            if [[ $confirm =~ ^[Ss]$ ]]; then
                echo ""
                print_title "INICIANDO TRANSCRIÇÃO..."
                echo "────────────────────────────────────────"
                
                show_loading 3 "🚀 Preparando transcrição"
                
                # Executar transcrição simples
                python transcribe.py "$selected_video"
                
                echo ""
                print_status "🎉 Transcrição concluída!"
                echo ""
                print_info "📄 Arquivo gerado na pasta 'temp/'"
            else
                print_info "Processamento cancelado"
            fi
            break
            ;;
        *)
            print_error "Escolha inválida. Digite 1, 2 ou 3."
            ;;
    esac
done

echo ""
print_title "🎉 PROCESSO FINALIZADO!"
echo "────────────────────────────────────────"
print_info "Obrigado por usar o Sistema de Transcrição Inteligente!"
echo ""
EOF

# Dar permissões executáveis
chmod +x ativar.sh
chmod +x run.sh
chmod +x interactive.sh
print_status "Scripts de facilitação criados e configurados"

echo ""
echo "=========================================="
echo "🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=========================================="
echo ""
echo "💡 FORMAS DE USAR O SISTEMA:"
echo ""
echo "   🚀 MODO FÁCIL (Recomendado):"
echo "      ./interactive.sh             # Interface guiada passo a passo"
echo ""
echo "   ⚡ MODO RÁPIDO:"
echo "      ./run.sh --complete video.mp4 1 1    # Execução automática"
echo "      ./run.sh --batch                     # Processar todos os vídeos"
echo ""
echo "   🔧 MODO AVANÇADO:"
echo "      source ativar.sh             # Ativar ambiente manualmente"
echo "      python transcribe.py ...     # Usar comandos Python diretos"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "   1. Coloque seus vídeos na pasta 'videos/'"
echo "   2. Execute: ./interactive.sh"
echo "   3. Siga as instruções na tela"
echo ""
echo "🆘 Se tiver dúvidas:"
echo "   • ./interactive.sh - Interface amigável"
echo "   • ./run.sh - Execução com verificações automáticas"
echo "   • cat PROJETO_TRANSCRICAO_AULAS.md - Documentação completa"
echo "" 