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
