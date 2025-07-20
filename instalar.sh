#!/bin/bash

# Script unificado para instalar TODAS as dependências do projeto
# Inclui: Python packages + FFmpeg + FFprobe

REQUIREMENTS_FILE="requirements.txt"

# Dependências totais do projeto (transcrição + produção)
PROJECT_DEPENDENCIES=(
    "groq"
    "google-generativeai"
    "pydantic"
)

# Função para verificar e adicionar dependência de forma segura
add_dependency() {
    local dependency=$1
    # Garante que a dependência seja adicionada em uma nova linha
    if ! grep -q "^${dependency}" "${REQUIREMENTS_FILE}"; then
        echo "Adicionando '${dependency}' ao ${REQUIREMENTS_FILE}..."
        # Adiciona uma nova linha no final do arquivo se não existir
        if [ -n "$(tail -c 1 ${REQUIREMENTS_FILE})" ]; then
            echo "" >> "${REQUIREMENTS_FILE}"
        fi
        echo "${dependency}" >> "${REQUIREMENTS_FILE}"
    else
        echo "Dependência '${dependency}' já existe em ${REQUIREMENTS_FILE}."
    fi
}

# Função para detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Função para detectar arquitetura
detect_arch() {
    case "$(uname -m)" in
        x86_64) echo "x64" ;;
        arm64|aarch64) echo "arm64" ;;
        *) echo "x64" ;; # fallback
    esac
}

# Função para baixar e instalar FFmpeg
install_ffmpeg() {
    echo "🎥 Instalando FFmpeg + FFprobe..."
    
    # Criar diretório bin se não existir
    mkdir -p bin
    
    local os=$(detect_os)
    local arch=$(detect_arch)
    local ffmpeg_url=""
    local ffmpeg_file=""
    
    if [[ "$os" == "linux" ]]; then
        if [[ "$arch" == "x64" ]]; then
            ffmpeg_url="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz"
            ffmpeg_file="ffmpeg-release-amd64-static.tar.xz"
        else
            ffmpeg_url="https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz"
            ffmpeg_file="ffmpeg-release-arm64-static.tar.xz"
        fi
    elif [[ "$os" == "macos" ]]; then
        if [[ "$arch" == "x64" ]]; then
            ffmpeg_url="https://evermeet.cx/ffmpeg/getrelease/zip"
            ffmpeg_file="ffmpeg-macos.zip"
        else
            ffmpeg_url="https://evermeet.cx/ffmpeg/getrelease/zip"
            ffmpeg_file="ffmpeg-macos.zip"
        fi
    fi
    
    if [[ -z "$ffmpeg_url" ]]; then
        echo "❌ Sistema operacional não suportado: $os $arch"
        echo "📥 Baixe FFmpeg manualmente em: https://ffmpeg.org/download.html"
        return 1
    fi
    
    echo "📥 Baixando FFmpeg para $os $arch..."
    
    # Baixar FFmpeg
    if curl -L -o "$ffmpeg_file" "$ffmpeg_url"; then
        echo "✅ Download concluído"
        
        # Extrair e instalar
        if [[ "$os" == "linux" ]]; then
            tar -xf "$ffmpeg_file"
            # Encontrar o diretório extraído
            local extracted_dir=$(find . -name "ffmpeg-*-static" -type d | head -1)
            if [[ -n "$extracted_dir" ]]; then
                cp "$extracted_dir/ffmpeg" bin/
                cp "$extracted_dir/ffprobe" bin/
                chmod +x bin/ffmpeg bin/ffprobe
                rm -rf "$extracted_dir" "$ffmpeg_file"
                echo "✅ FFmpeg + FFprobe instalados em bin/"
            else
                echo "❌ Erro ao extrair FFmpeg"
                return 1
            fi
        elif [[ "$os" == "macos" ]]; then
            unzip -q "$ffmpeg_file"
            # Encontrar os executáveis
            if [[ -f "ffmpeg" ]]; then
                mv ffmpeg bin/
                mv ffprobe bin/ 2>/dev/null || echo "⚠️  FFprobe não encontrado no zip"
                chmod +x bin/ffmpeg bin/ffprobe 2>/dev/null
                rm -f "$ffmpeg_file"
                echo "✅ FFmpeg instalado em bin/"
            else
                echo "❌ Erro ao extrair FFmpeg"
                return 1
            fi
        fi
    else
        echo "❌ Erro ao baixar FFmpeg"
        echo "📥 Baixe manualmente em: https://ffmpeg.org/download.html"
        return 1
    fi
}

# --- Início da Execução ---

echo "🚀 INSTALADOR COMPLETO - Sistema de Edição de Vídeos AI"
echo "=================================================="

# Verificar se estamos no diretório correto
if [[ ! -f "content_pipeline.py" ]]; then
    echo "❌ ERRO: content_pipeline.py não encontrado!"
    echo "   Execute este instalador na pasta raiz do projeto."
    exit 1
fi

echo "Verificando e preparando dependências..."

# Garante que o arquivo requirements.txt exista
touch "${REQUIREMENTS_FILE}"

# Adiciona as dependências necessárias ao arquivo
for dep in "${PROJECT_DEPENDENCIES[@]}"; do
    add_dependency "$dep"
done

# Criar estrutura de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p videos temp bin

# Instalar FFmpeg + FFprobe
if [[ ! -f "bin/ffmpeg" ]] || [[ ! -f "bin/ffprobe" ]]; then
    install_ffmpeg
else
    echo "✅ FFmpeg + FFprobe já instalados"
fi

# Instalar todas as dependências do arquivo
echo "\n📦 Instalando/atualizando todas as dependências Python..."

# Verifica se o ambiente virtual existe para dar um feedback melhor
if [ -f .venv/bin/activate ]; then
    echo "Ativando ambiente virtual .venv..."
    source .venv/bin/activate
    
    # Comando de instalação corrigido
    pip install -r requirements.txt
    
    deactivate
    echo "\nAmbiente virtual desativado."
else
    echo "\nAVISO: Ambiente virtual .venv não encontrado."
    echo "Instalando dependências globalmente. É altamente recomendado usar um ambiente virtual."
    
    # Comando de instalação corrigido
    pip install -r requirements.txt
fi

# Criar arquivo .env de exemplo
echo "🔑 Criando arquivo .env de exemplo..."
cat > .env << 'EOF'
# APIs obrigatórias
GROQ_API_KEY=sua_chave_groq_aqui
GEMINI_API_KEY=sua_chave_gemini_aqui

# Configurações de qualidade
CHUNK_SIZE_SECONDS=600
GEMINI_THINKING=true
GEMINI_MAX_CONTEXT=1000000

# Performance
MAX_RETRIES=3
REQUEST_TIMEOUT=300
DEBUG_MODE=false

# Configurações YouTube
SUBTITLE_LANGUAGES=pt,en,es
IMAGE_GENERATION_MODELS=gemini,imagen-3,imagen-4,imagen-4-ultra
THUMBNAIL_VIDEO_COUNT=3
THUMBNAIL_SHORTS_COUNT=2
EOF

echo "✅ Arquivo .env criado"

# Testar instalação
echo "\n🧪 Testando instalação..."

# Testar FFmpeg
if [[ -f "bin/ffmpeg" ]]; then
    if bin/ffmpeg -version >/dev/null 2>&1; then
        echo "✅ FFmpeg: Funcionando"
    else
        echo "❌ FFmpeg: Erro na execução"
    fi
else
    echo "❌ FFmpeg: Não encontrado"
fi

# Testar FFprobe
if [[ -f "bin/ffprobe" ]]; then
    if bin/ffprobe -version >/dev/null 2>&1; then
        echo "✅ FFprobe: Funcionando"
    else
        echo "❌ FFprobe: Erro na execução"
    fi
else
    echo "⚠️  FFprobe: Não encontrado (sistema usará fallback com FFmpeg)"
fi

# Testar Python
if python content_pipeline.py --help >/dev/null 2>&1; then
    echo "✅ Sistema Python: Funcionando"
else
    echo "❌ Sistema Python: Erro na execução"
fi

echo "\n=================================================="
echo "🎉 INSTALAÇÃO COMPLETA CONCLUÍDA!"
echo "=================================================="
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. 🔑 Configure suas APIs:"
echo "   cp .env.exemplo .env"
echo "   nano .env  # Edite com suas chaves reais"
echo ""
echo "2. 📹 Coloque seus vídeos na pasta videos/"
echo ""
echo "3. 🚀 Execute o sistema:"
echo "   ./ativar.sh  # Para ativar o ambiente"
echo "   python content_pipeline.py  # Para iniciar"
echo ""
echo "4. 📚 Consulte o README.md para instruções detalhadas"
echo ""
echo "✅ Sistema pronto para uso!"