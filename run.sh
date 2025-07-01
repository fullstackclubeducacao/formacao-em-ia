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
