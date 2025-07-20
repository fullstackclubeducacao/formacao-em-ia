#!/bin/bash

# Script unificado para instalar todas as dependências do projeto

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

# --- Início da Execução ---

echo "Verificando e preparando dependências..."

# Garante que o arquivo requirements.txt exista
touch "${REQUIREMENTS_FILE}"

# Adiciona as dependências necessárias ao arquivo
for dep in "${PROJECT_DEPENDENCIES[@]}"; do
    add_dependency "$dep"
done

# Instala todas as dependências do arquivo
echo "\nInstalando/atualizando todas as dependências do projeto..."

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

echo "\n✅ Instalação concluída! O ambiente está pronto."