#!/bin/bash

# Sistema Unificado de Produção de Conteúdo Educacional
# Carrega o ativador principal que configura o ambiente e as chaves de API

if [ -f "./ativar.sh" ]; then
    source ./ativar.sh
else
    echo "ERRO: Arquivo ativar.sh não encontrado. Execute o script da raiz do projeto."
    exit 1
fi

echo "🤖 Sistema Unificado de Produção de Conteúdo Educacional"
echo "========================================================"
echo "✅ Ambiente virtual ativado"
echo "✅ Variáveis de ambiente carregadas"
echo ""
echo "🎯 Sistema pronto! Comandos disponíveis:"
echo "   python content_pipeline.py                    # Menu interativo"
echo "   python content_pipeline.py --complete video.mp4 1 1 # Completo"
echo "   python content_pipeline.py --batch            # Lote"
echo "   python content_pipeline.py --youtube aula_dir # YouTube apenas"
echo ""

# Executa o sistema unificado
python3 content_pipeline.py

echo ""
echo "🏁 Sistema finalizado."