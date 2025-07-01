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
