# 🎙️ Sistema de Transcrição Inteligente para Alunos

## 📖 Visão Geral do Projeto

Bem-vindos ao **Sistema de Transcrição Inteligente** da **Full Stack Club**! Este é um sistema completo e automatizado que converte suas videoaulas em conteúdo estruturado e documentação organizada.

### ✨ O que o sistema faz?

- 🎯 **Transcreve vídeos** com precisão ultra-alta usando **Groq Whisper**
- 🧠 **Analisa conteúdo** com **Gemini AI** para extrair insights
- 📄 **Gera documentação** automática em README.md estruturado
- 🏗️ **Organiza por módulos** e aulas automaticamente
- 💡 **Extrai conceitos**, tecnologias e comandos importantes
- 🎯 **Cria objetivos** de aprendizado e pré-requisitos

---

## ⚡ Quick Start (3 minutos)

Para os **impacientes** que querem começar **AGORA**:

### 🚀 Método SUPER FÁCIL (Recomendado)

```bash
# 1. Instalar (escolha seu sistema)
# Windows:
instalar.bat

# Mac/Linux:
./instalar.sh

# 2. Usar modo interativo (faz tudo automaticamente!)
./interactive.sh

# 3. Seguir instruções na tela - pronto! 🎉
```

### ⚡ Método RÁPIDO (Usuários Experientes)

```bash
# 1. Instalar
./instalar.sh

# 2. Processar um vídeo específico
./run.sh --complete "videos/minha_aula.mp4" 1 1

# 3. Ou processar todos os vídeos
./run.sh --batch

# 4. Ver resultado em: modulo-01/aula-01-*/README.md 
```

### 🔧 Método MANUAL (Compatibilidade)

```bash
# 1. Instalar
./instalar.sh

# 2. Ativar ambiente manualmente
source ativar.sh

# 3. Processar com comando Python direto
python transcribe.py --complete "videos/minha_aula.mp4" 1 1
```

### 🔑 APIs Necessárias

- **🎙️ Groq API** (obrigatória): [console.groq.com](https://console.groq.com/keys)
- **🧠 Gemini API** (opcional): [ai.google.dev](https://ai.google.dev/)

**💡 Dica:** Groq é grátis para começar! Gemini opcional mas recomendado para análises.

---

## 🚀 Guia Completo de Instalação

### Pré-requisitos

- **Python 3.8+** (Windows/Mac/Linux)
- **Conexão com internet** para instalação
- **Chave API Groq** (obrigatória) - [Obter aqui](https://console.groq.com/keys)
- **Chave API Gemini** (opcional) - [Obter aqui](https://ai.google.dev/)

### 📥 1. Download do Projeto

**Opção A: Clone do Git**
```bash
git clone https://github.com/fullstackclubeducacao/formacao-em-ia.git
cd formacao-em-ia
```

**Opção B: Download ZIP**
1. Baixe o projeto em ZIP
2. Extraia em uma pasta de sua escolha
3. Abra o terminal/prompt na pasta

### 🔧 2. Instalação Automática

**Para Windows:**
```cmd
instalar.bat
```

**Para Mac/Linux:**
```bash
chmod +x instalar.sh
./instalar.sh
```

O instalador fará **automaticamente**:
- ✅ Verificação do Python
- ✅ Criação de ambiente virtual
- ✅ Instalação de dependências
- ✅ Configuração de diretórios
- ✅ Verificação do FFmpeg (incluído no projeto)
- ✅ Configuração inicial

### 🔑 3. Configuração das APIs

1. **Copie o arquivo de configuração:**
```bash
cp .env.exemplo .env
```

2. **Edite o arquivo `.env`** com suas chaves:
```bash
# 🎙️ GROQ API (OBRIGATÓRIA)
GROQ_API_KEY=sua_chave_groq_real

# 🧠 GEMINI API (OPCIONAL)
GEMINI_API_KEY=sua_chave_gemini_real
```

3. **Carregue as variáveis:**

**Windows:**
```cmd
set-variables.bat
```

**Mac/Linux:**
```bash
source .env
```

---

## 🎯 Como Usar o Sistema

### 🚀 Scripts Facilitados (NOVO!)

O sistema agora inclui **scripts inteligentes** que eliminam a necessidade de ativar ambiente virtual manualmente:

**🎯 Por que usar os scripts facilitados?**
- ❌ **ANTES:** `source .venv/bin/activate` + `source .env` + comando Python
- ✅ **AGORA:** `./interactive.sh` ou `./run.sh` + parâmetros

**⚡ Benefícios:**
- ✅ **Zero configuração manual** de ambiente
- ✅ **Verificações automáticas** do sistema
- ✅ **Mensagens de erro claras** e soluções
- ✅ **Interface amigável** para iniciantes
- ✅ **Compatibilidade total** com sistema original

#### 🎯 **`./interactive.sh`** - Modo Guiado (RECOMENDADO)
```bash
./interactive.sh
```
**✨ Funcionalidades:**
- ✅ Interface colorida e interativa
- ✅ Configuração automática das APIs
- ✅ Seleção visual de vídeos
- ✅ Guia passo a passo completo
- ✅ Verificações automáticas do sistema
- ✅ Não precisa lembrar comandos!

#### ⚡ **`./run.sh`** - Execução Automática
```bash
# Processar um vídeo específico
./run.sh --complete "videos/aula.mp4" 1 1

# Processar todos os vídeos
./run.sh --batch

# Apenas transcrever
./run.sh "videos/aula.mp4"
```
**✨ Funcionalidades:**
- ✅ Ativa ambiente virtual automaticamente
- ✅ Carrega variáveis de ambiente
- ✅ Verifica configurações
- ✅ Executa com parâmetros simplificados

#### 🔧 **`source ativar.sh`** - Ativação Manual
```bash
source ativar.sh
python transcribe.py --complete "videos/aula.mp4" 1 1
```
**✨ Para usuários que preferem controle total**

### 📹 Preparação dos Vídeos

1. **Coloque seus vídeos** na pasta `videos/`
2. **Formatos aceitos:** MP4, AVI, MOV, MKV, WEBM, M4V
3. **Nomeação recomendada:** `modulo-01-aula-02-tema.mp4`

### 🚀 Modos de Operação Tradicionais

Para usuários avançados, o sistema ainda oferece **3 modos principais** via Python:

#### **Modo 1: 🔄 Transcrição Simples (Compatibilidade)**
```bash
python transcribe.py videos/minha_aula.mp4
```
**Características:**
- ✅ Apenas transcrição com Groq Whisper
- ✅ 100% compatível com sistema original
- ✅ Resultado salvo em `temp/minha_aula_transcription.json`
- ⚠️  Sem análise de IA ou documentação

#### **Modo 2: ⭐ Análise Completa (Recomendado)**
```bash
python transcribe.py --complete videos/minha_aula.mp4 1 3
#                                                           ↑ ↑
#                                                    módulo  aula
```
**Características:**
- ✅ Transcrição + análise inteligente com Gemini
- ✅ README.md automático estruturado
- ✅ Organização modular: `modulo-01/aula-03-*/`
- ✅ Extração de conceitos, tecnologias e comandos
- ✅ Documentação educacional completa

**Parâmetros:**
- `videos/minha_aula.mp4` - Caminho do vídeo
- `1` - Número do módulo (opcional, padrão: 1)
- `3` - Número da aula (opcional, padrão: 1)

#### **Modo 3: 🚀 Processamento em Lote (Produção)**
```bash
python transcribe.py --batch videos 1
#                            ↑      ↑
#                        pasta   módulo inicial
```
**Características:**
- ✅ Processa TODOS os vídeos automaticamente
- ✅ Detecção inteligente de módulos/aulas por nome do arquivo
- ✅ Numeração sequencial automática
- ✅ Relatório completo de processamento
- ✅ Ideal para cursos completos

**Parâmetros:**
- `videos` - Pasta com vídeos (opcional, padrão: "videos")
- `1` - Módulo inicial (opcional, padrão: 1)

#### **📋 Modo de Ajuda**
```bash
python transcribe.py --help
# ou simplesmente:
python transcribe.py
```

### 📁 Estrutura Gerada

Para cada aula processada:
```
modulo-01/
└── aula-02-introducao-python/
    ├── README.md           # 📄 Documentação completa
    ├── transcricao.json    # 🎙️ Dados da transcrição
    ├── analise.json        # 🧠 Análise da IA
    ├── assets/             # 📊 Recursos extras
    └── scripts/            # 💻 Comandos extraídos
        └── comandos.md
```

### 📄 Conteúdo do README.md Gerado

Cada aula recebe um README.md completo com:

- **📚 Título e Descrição**
- **⏱️ Duração e Dificuldade**
- **🎯 Objetivos de Aprendizado**
- **📋 Pré-requisitos**
- **🔑 Pontos-Chave**
- **🛠️ Tecnologias Mencionadas**
- **💻 Comandos e Códigos**
- **💡 Conceitos Importantes**
- **🏷️ Tags para Busca**
- **📝 Transcrição Completa**

---

## ⚙️ Configurações Avançadas

### 🎛️ Variáveis de Ambiente

Todas configuráveis no arquivo `.env`:

#### **🎙️ Configurações do Groq**
```bash
GROQ_MODEL=whisper-large-v3-turbo    # Modelo de transcrição
GROQ_LANGUAGE=pt                      # Idioma (pt, en, es, fr...)
```

#### **🧠 Configurações do Gemini**
```bash
GEMINI_MODEL=gemini-2.5-flash         # Modelo de análise
GEMINI_THINKING=true                  # Thinking habilitado
GEMINI_THINKING_BUDGET=-1             # Budget dinâmico
GEMINI_MAX_CONTEXT=1000000            # 1M tokens contexto
```

#### **🔧 Configurações de Sistema**
```bash
REQUEST_TIMEOUT=300                   # 5 minutos timeout
MAX_RETRIES=3                         # 3 tentativas máximas
DEBUG_MODE=false                      # Logs detalhados
SAVE_DEBUG_FILES=false                # Salvar arquivos debug
```

#### **🎵 Configurações de Áudio**
```bash
CHUNK_SIZE_SECONDS=600                # 10 minutos por chunk
AUDIO_SAMPLE_RATE=16000               # 16kHz qualidade
AUDIO_CHANNELS=1                      # Mono
AUDIO_FORMAT=flac                     # Formato FLAC
```

### 🎯 Presets de Configuração

#### **Configuração Rápida (Econômica)**
```bash
GEMINI_MODEL=gemini-2.5-flash
GEMINI_THINKING=false
GEMINI_MAX_CONTEXT=100000
CHUNK_SIZE_SECONDS=300
```

#### **Configuração Qualidade (Recomendada)**
```bash
GEMINI_MODEL=gemini-2.5-pro
GEMINI_THINKING=true
GEMINI_THINKING_BUDGET=-1
GEMINI_MAX_CONTEXT=1000000
```

---

## 🛠️ Solução de Problemas

### 🚀 SOLUÇÃO DEFINITIVA: Use os Scripts Facilitados!

**❌ Problema mais comum:** "Groq não instalado" ou "Módulo não encontrado"
**✅ Causa:** Ambiente virtual não ativado ou configuração incorreta
**🎯 Solução:** Use SEMPRE os scripts facilitados!

```bash
# ❌ NÃO FAÇA MAIS ISSO:
python transcribe.py video.mp4

# ✅ FAÇA ASSIM:
./interactive.sh    # Modo fácil
# ou
./run.sh --complete video.mp4 1 1    # Modo rápido
```

### ❌ Problemas Comuns (Modo Manual)

#### **Erro: "GROQ_API_KEY não encontrada"**
```bash
# SOLUÇÃO FÁCIL:
./interactive.sh    # Configura tudo automaticamente

# SOLUÇÃO MANUAL:
source .env
```

#### **Erro: "FFmpeg não encontrado"**
```bash
# SOLUÇÃO FÁCIL:
./run.sh video.mp4    # Verifica automaticamente

# SOLUÇÃO MANUAL:
chmod +x ./bin/ffmpeg ./bin/ffprobe
```

#### **Erro: "Módulo não encontrado"**
```bash
# SOLUÇÃO FÁCIL:
./interactive.sh    # Detecta e resolve automaticamente

# SOLUÇÃO MANUAL:
source .venv/bin/activate
python -m pip install -r requirements.txt
```

#### **Timeout na análise**
```bash
# Aumente timeout no .env:
REQUEST_TIMEOUT=600
MAX_RETRIES=5
```

### 🐛 Modo Debug

Para diagnosticar problemas:
```bash
# Ative debug no .env:
DEBUG_MODE=true
SAVE_DEBUG_FILES=true

# Execute e verifique logs em temp/debug/
```

---

## 📊 Monitoramento e Custos

### 💰 Custos Estimados (USD)

**Groq (Transcrição):**
- ~$0.27 por hora de áudio
- Muito econômico

**Gemini (Análise):**
- Flash: ~$0.075 por 1M tokens
- Pro: ~$1.25 por 1M tokens
- Thinking: tokens extras conforme budget

### 📈 Performance

- **Transcrição:** 2-5x tempo real
- **Análise:** 30-120 segundos
- **Vídeos longos:** Até 3-4 horas sem problemas

---

## 🎓 Exemplos Práticos

### **Exemplo 1: 🎯 Primeira Vez - Modo Super Fácil**
```bash
# 1. Executar modo interativo (faz tudo automaticamente!)
./interactive.sh

# 2. Seguir as instruções na tela:
#    ✅ Sistema verifica instalação
#    ✅ Configura APIs automaticamente
#    ✅ Lista vídeos disponíveis
#    ✅ Seleciona modo de processamento
#    ✅ Confirma configurações
#    ✅ Executa processamento

# 3. Resultado criado automaticamente:
# modulo-01/aula-01-introducao-ao-python/
#   ├── README.md              # 📄 Documentação automática
#   ├── transcricao.json       # 🎙️ Dados de transcrição
#   ├── analise.json          # 🧠 Análise da IA
#   ├── assets/               # 📊 Recursos
#   └── scripts/              # 💻 Comandos extraídos
#       └── comandos.md
```

### **Exemplo 2: ⚡ Processamento Rápido Individual**
```bash
# Modo rápido para usuários experientes
./run.sh --complete "videos/Introducao ao Python.mp4" 1 1

# Sistema faz automaticamente:
# ✅ Ativa ambiente virtual
# ✅ Carrega variáveis .env
# ✅ Verifica configurações
# ✅ Processa com análise completa
```

### **Exemplo 3: 🎯 Primeira Aula - Modo Manual (Avançado)**
```bash
# 1. Ativar ambiente virtual
source ativar.sh

# 2. Processar aula com análise completa
python transcribe.py --complete "videos/Introducao ao Python.mp4" 1 1

# 3. Resultado criado automaticamente (mesmo resultado dos outros modos)
```

### **Exemplo 4: 🚀 Processamento de Curso Completo - Modo Fácil**
```bash
# Estrutura dos vídeos na pasta:
# videos/
#   ├── modulo-01-aula-01-python-intro.mp4
#   ├── modulo-01-aula-02-variaveis.mp4  
#   ├── modulo-02-aula-01-funcoes.mp4
#   └── modulo-02-aula-02-classes.mp4

# OPÇÃO A: Modo interativo (recomendado)
./interactive.sh
# ✅ Escolher "Modo Lote" na interface
# ✅ Sistema processa todos automaticamente

# OPÇÃO B: Modo rápido
./run.sh --batch

# OPÇÃO C: Modo manual (avançado)
source ativar.sh
python transcribe.py --batch videos 1

# Resultado organizado (qualquer opção):
# modulo-01/
#   ├── aula-01-python-intro/
#   └── aula-02-variaveis/
# modulo-02/
#   ├── aula-01-funcoes/
#   └── aula-02-classes/
```

### **Exemplo 5: 📹 Modo Simples (Apenas Transcrição)**
```bash
# OPÇÃO A: Modo interativo
./interactive.sh
# ✅ Escolher "Modo Simples" na interface

# OPÇÃO B: Modo rápido
./run.sh "videos/Workshop Docker.mp4"

# OPÇÃO C: Modo manual (para compatibilidade)
source ativar.sh
python transcribe.py "videos/Workshop Docker.mp4"

# Resultado em: temp/Workshop Docker_transcription.json
```

### **Exemplo 4: ⚙️ Configuração Avançada Premium**
```bash
# Criar configuração premium no .env:
echo "GEMINI_MODEL=gemini-2.5-pro" >> .env
echo "GEMINI_THINKING_BUDGET=32768" >> .env
echo "DEBUG_MODE=true" >> .env

# Recarregar configurações
source .env

# Processar com qualidade máxima
python transcribe.py --complete "videos/Aula Avancada IA.mp4" 3 5
```

### **Exemplo 5: 🎯 Diferentes Formatos e Idiomas**
```bash
# O sistema aceita múltiplos formatos
python transcribe.py --complete "videos/aula.mp4" 1 1     # MP4
python transcribe.py --complete "videos/demo.avi" 1 2     # AVI  
python transcribe.py --complete "videos/live.mkv" 1 3     # MKV

# Vídeos em outros idiomas
export GROQ_LANGUAGE=en
python transcribe.py --complete "videos/English Lesson.mp4" 1 1

export GROQ_LANGUAGE=es
python transcribe.py --complete "videos/Leccion Espanol.mp4" 1 1
```

### **Exemplo 6: 🔄 Processamento com Retry e Debug**
```bash
# Para vídeos com problemas de rede
export MAX_RETRIES=5
export REQUEST_TIMEOUT=600
export DEBUG_MODE=true
export SAVE_DEBUG_FILES=true

python transcribe.py --complete "videos/video_longo.mp4" 2 1

# Arquivos de debug salvos em:
# temp/debug/
#   ├── ffmpeg_chunk_1_output.log
#   ├── transcription_chunk_1.json
#   └── gemini_analysis_debug.json
```

### **Exemplo 7: 🎮 Script de Automação Completa**
```bash
#!/bin/bash
# Script completo para processar curso

# Ativar ambiente
source .venv/bin/activate
source .env

# Processar módulo por módulo
echo "🚀 Processando Módulo 1: Python Básico"
python transcribe.py --batch videos/modulo-01 1

echo "🚀 Processando Módulo 2: Python Avançado"  
python transcribe.py --batch videos/modulo-02 2

echo "🚀 Processando Módulo 3: Projetos"
python transcribe.py --batch videos/modulo-03 3

echo "✅ Curso completo processado!"
ls -la modulo-*/
```

---

## 🔧 Personalização

### 📁 Mudando Estrutura de Pastas

No arquivo `.env`:
```bash
OUTPUT_BASE_DIR=curso-{modulo:02d}              # curso-01/
AULA_DIR_PATTERN=licao-{numero:02d}-{slug}      # licao-01-introducao/
```

### 🎯 Adicionando Idiomas

```bash
GROQ_LANGUAGE=en                                # Inglês
GROQ_LANGUAGE=es                                # Espanhol
GROQ_LANGUAGE=fr                                # Francês
```

### 🎵 Otimizando Qualidade de Áudio

```bash
AUDIO_SAMPLE_RATE=22050                         # Maior qualidade
AUDIO_FORMAT=wav                                # Formato alternativo
CHUNK_SIZE_SECONDS=300                          # Chunks menores = mais precisão
```

---

## 📚 Referência Rápida de Comandos

### 🚀 Scripts Facilitados (NOVOS - Recomendados!)

| Comando | Descrição | Características |
|---------|-----------|-----------------|
| **`./interactive.sh`** | Modo guiado interativo | ✅ Interface passo a passo<br>✅ Configuração automática de APIs<br>✅ Verificações do sistema |
| **`./run.sh --complete video.mp4 1 1`** | Execução automática completa | ✅ Ativa ambiente automaticamente<br>✅ Transcrição + análise + docs |
| **`./run.sh --batch`** | Processamento em lote automático | ✅ Processa todos os vídeos<br>✅ Configuração automática |
| **`./run.sh video.mp4`** | Transcrição simples automática | ✅ Apenas transcrição<br>✅ Sem necessidade de configuração manual |

### 🔧 Comandos Python Tradicionais (Avançados)

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| **Transcrição Simples** | Apenas transcrição básica | `python transcribe.py video.mp4` |
| **Análise Completa** | Transcrição + IA + Docs | `python transcribe.py --complete video.mp4 1 1` |
| **Processamento em Lote** | Todos os vídeos de uma pasta | `python transcribe.py --batch videos 1` |
| **Ajuda** | Mostrar todas as opções | `python transcribe.py --help` |

### 🔧 Configuração e Uso Rápido

| Tarefa | Comando Facilitado | Comando Manual |
|--------|--------------------|----------------|
| **Instalar (Windows)** | `instalar.bat` | - |
| **Instalar (Mac/Linux)** | `./instalar.sh` | - |
| **Usar Primeira Vez** | `./interactive.sh` | `source ativar.sh` + configs |
| **Processar Um Vídeo** | `./run.sh --complete video.mp4 1 1` | `source ativar.sh` + `python transcribe.py --complete video.mp4 1 1` |
| **Processar Todos** | `./run.sh --batch` | `source ativar.sh` + `python transcribe.py --batch` |
| **Apenas Transcrever** | `./run.sh video.mp4` | `source ativar.sh` + `python transcribe.py video.mp4` |
| **Configurar APIs** | Via `./interactive.sh` | Editar arquivo `.env` |

### ⚙️ Variáveis de Ambiente Essenciais

| Variável | Valor Padrão | Descrição |
|----------|--------------|-----------|
| `GROQ_API_KEY` | - | **Obrigatória** - Chave API Groq |
| `GEMINI_API_KEY` | - | **Opcional** - Chave API Gemini |
| `GROQ_MODEL` | `whisper-large-v3-turbo` | Modelo de transcrição |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Modelo de análise |
| `GROQ_LANGUAGE` | `pt` | Idioma (pt, en, es, fr...) |
| `DEBUG_MODE` | `false` | Ativar logs detalhados |

### 🎯 Estrutura de Arquivos

```
📁 Projeto/
├── 📄 transcribe.py           # Sistema principal Python
├── 🚀 interactive.sh          # Modo fácil interativo (NOVO!)
├── ⚡ run.sh                  # Execução automática (NOVO!)
├── 🔧 ativar.sh               # Ativação manual
├── 📄 instalar.sh/.bat        # Instaladores
├── 📄 .env                    # Suas configurações
├── 📄 .env.exemplo            # Template de configuração
├── 📖 COMO_USAR.md            # Guia super simples (NOVO!)
├── 📁 videos/                 # Coloque seus vídeos aqui
├── 📁 temp/                   # Arquivos temporários
├── 📁 modulo-XX/              # Aulas organizadas
│   └── 📁 aula-XX-nome/
│       ├── 📄 README.md       # Documentação
│       ├── 📄 transcricao.json
│       └── 📄 analise.json
└── 📁 bin/                    # FFmpeg incluído
```

## 📚 Recursos Adicionais

### 🔗 Links Úteis

- **🎙️ Groq Console:** https://console.groq.com/
- **🧠 Google AI Studio:** https://ai.google.dev/
- **🎥 Documentação FFmpeg:** https://ffmpeg.org/documentation.html
- **📖 Repositório do Projeto:** https://github.com/seu-repo/formacao-em-ia

### 📖 Documentação Técnica

- **📋 GUIA_TRANSCRICAO.md** - Guia técnico detalhado
- **💻 transcribe.py** - Código fonte comentado
- **📦 requirements.txt** - Dependências Python
- **🔧 .env.exemplo** - Template de configuração

### 🎯 Casos de Uso

- **📚 Educação:** Cursos online, aulas gravadas, workshops
- **🏢 Corporativo:** Treinamentos, reuniões, apresentações
- **🎥 Content Creators:** YouTube, podcasts, webinars, lives

---

## 🤝 Suporte e Comunidade

### 💬 Como Obter Ajuda

1. **📖 Consulte este guia** primeiro
2. **🐛 Ative modo debug** para diagnóstico
3. **💬 Comunidade Full Stack Club** para dúvidas
4. **📧 Issues no GitHub** para bugs

### 🔄 Atualizações

O sistema é atualizado regularmente:
- **v2.0.0** - Sistema atual com Gemini 2.5
- **v2.1.0** - Context caching (em desenvolvimento)
- **v2.2.0** - Interface web (planejado)

---

## 🎉 Conclusão

Agora você tem um sistema completo de transcrição e análise **com interface super amigável**! 

### ✅ Próximos Passos:

1. **🚀 Execute o instalador:** `./instalar.sh`
2. **🎯 Use o modo fácil:** `./interactive.sh`
3. **📖 Siga as instruções** na tela colorida
4. **🎉 Pronto!** Seus vídeos viram documentação automática

### 🎯 3 Formas de Usar:

- **🚀 FÁCIL:** `./interactive.sh` - Interface guiada (recomendado)
- **⚡ RÁPIDO:** `./run.sh --complete video.mp4 1 1` - Execução direta
- **🔧 AVANÇADO:** `source ativar.sh` + Python - Controle total

### 🎯 Lembre-se:

- **✅ Scripts facilitados** eliminam problemas de ambiente virtual
- **✅ Interface interativa** configura APIs automaticamente
- **✅ Verificações automáticas** detectam e resolvem problemas
- **✅ Groq é obrigatório** para transcrição
- **✅ Gemini é opcional** mas recomendado para análise
- **✅ Sistema funciona offline** após instalação (exceto APIs)
- **✅ FFmpeg incluído** no projeto
- **✅ Cross-platform** Windows/Mac/Linux
- **✅ Documentação completa** em `COMO_USAR.md`

---

**⭐ Sistema Enhanced Transcription v2.0.0 - Full Stack Club**

*Transformando videoaulas em conhecimento estruturado e pesquisável!*

---

## 📄 Licença e Créditos

- **Desenvolvido para:** Full Stack Club
- **Tecnologias:** Python, Groq Whisper, Google Gemini AI, FFmpeg
- **Compatibilidade:** Windows 10+, macOS 10.14+, Linux Ubuntu 18.04+
- **Licença:** Uso educacional - Full Stack Club

*Para dúvidas técnicas, consulte o GUIA_TRANSCRICAO.md ou entre em contato com a comunidade.* 