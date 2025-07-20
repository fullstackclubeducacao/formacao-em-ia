# 🤖 Sistema Unificado de Produção de Conteúdo Educacional

## 📋 Visão Geral

Sistema completo e automatizado que converte suas videoaulas em conteúdo estruturado, documentação organizada e funcionalidades YouTube prontas para publicação.

### ✨ O que o sistema faz?

- 🎯 **Transcreve vídeos** com precisão ultra-alta usando **Groq Whisper**
- 🧠 **Analisa conteúdo** com **Gemini AI** para extrair insights
- 📄 **Gera documentação** automática em README.md estruturado
- 🏗️ **Organiza por módulos** e aulas automaticamente
- 💡 **Extrai conceitos**, tecnologias e comandos importantes
- 🎬 **Cria conteúdo YouTube** (legendas, capítulos, shorts, thumbnails, metadados)

---

## 🚀 Início Rápido (3 minutos)

### 1️⃣ **Instalação (Uma vez apenas)**

```bash
# Windows:
instalar.bat

# Mac/Linux:
./instalar.sh
```

### 2️⃣ **Configuração das APIs**

```bash
# Copie o arquivo de exemplo
cp _env .env

# Edite com suas chaves reais
nano .env
```

**APIs necessárias:**
- **🎙️ Groq API** (obrigatória): [console.groq.com](https://console.groq.com/keys)
- **🧠 Gemini API** (opcional): [ai.google.dev](https://ai.google.dev/)

### 3️⃣ **Usar o Sistema**

```bash
# Modo interativo (RECOMENDADO)
python3 content_pipeline.py

# Ou use o script facilitado
./produzir_conteudo.sh
```

---

## 🎯 Funcionalidades Disponíveis

### 📹 **Processamento de Vídeos**
- **Transcrição inteligente** com Groq Whisper
- **Análise de conteúdo** com Gemini AI
- **Documentação automática** (README.md, JSON, scripts)
- **Organização modular** por módulos e aulas

### 🎬 **Funcionalidades YouTube (Opcionais)**
- **📝 Legendas SRT** em PT/EN/ES (escolha idiomas)
- **📖 Capítulos** para YouTube (geração automática)
- **✂️ YouTube Shorts** (clips de 30-60 segundos)
- **📋 Metadados SEO** (títulos, descrições, tags)
- **🎨 Thumbnails com IA** (Gemini/Imagen, formatos 16:9 e 9:16)

---

## 🚀 Como Usar

### 🎯 **Modo Interativo (Recomendado)**

```bash
python3 content_pipeline.py
```

**Menu disponível:**
1. **📹 INDIVIDUAL** - Processar um vídeo específico
2. **📦 LOTE** - Processar todos os vídeos
3. **🎬 YOUTUBE** - Adicionar funcionalidades YouTube a aulas existentes
4. **⚡ SIMPLES** - Apenas transcrição
5. **⚙️ STATUS** - Verificar configurações

### ⚡ **Linha de Comando**

```bash
# Processamento completo
python3 content_pipeline.py --complete video.mp4 1 1

# Processamento em lote
python3 content_pipeline.py --batch

# Funcionalidades YouTube (aula existente)
python3 content_pipeline.py --youtube modulo-01/aula-01-exemplo

# Compatibilidade (só transcrição)
python3 content_pipeline.py video.mp4
```

---

## 📁 Estrutura Gerada

```
modulo-01/
└── aula-01-exemplo/
    ├── 📄 README.md                 # Documentação completa
    ├── 📊 transcricao.json          # Transcrição detalhada
    ├── 🧠 analise.json              # Análise estruturada
    ├── 📝 legenda_pt.srt           # Legendas (opcional)
    ├── 📝 legenda_en.srt           # Legendas (opcional)
    ├── 📝 legenda_es.srt           # Legendas (opcional)
    ├── 📖 capitulos.txt            # Capítulos YouTube (opcional)
    ├── 📋 metadata_youtube.txt     # Metadados SEO (opcional)
    ├── 📂 scripts/                 # Comandos extraídos
    ├── 📂 shorts/                  # YouTube Shorts (opcional)
    │   ├── corte_1/
    │   │   ├── short_final.mp4
    │   │   ├── legenda_short.srt
    │   │   └── info.txt
    │   └── corte_2/
    └── 📂 thumbnails/              # Thumbnails IA (opcional)
        ├── video/                  # 16:9 para vídeo principal
        └── shorts/                 # 9:16 para shorts
```

---

## ⚙️ Configurações

### 🔑 **Variáveis de Ambiente (.env)**

```bash
# APIs obrigatórias
GROQ_API_KEY=sua_chave_groq        # Transcrição
GEMINI_API_KEY=sua_chave_gemini    # Análise e YouTube

# Configurações de qualidade
CHUNK_SIZE_SECONDS=600             # Tamanho dos chunks (10min)
GEMINI_THINKING=true               # Análise mais profunda
GEMINI_MAX_CONTEXT=1000000         # Contexto máximo (1M tokens)

# Performance
MAX_RETRIES=3                      # Tentativas em caso de erro
REQUEST_TIMEOUT=300                # Timeout (5 minutos)
DEBUG_MODE=false                   # Logs detalhados
```

### 🎬 **Configurações YouTube**

```bash
# Idiomas das legendas (escolha: pt, en, es)
SUBTITLE_LANGUAGES=pt,en,es

# Modelos de thumbnail disponíveis
IMAGE_GENERATION_MODELS=gemini,imagen-3,imagen-4,imagen-4-ultra

# Quantidade de thumbnails
THUMBNAIL_VIDEO_COUNT=3            # 1-5 para vídeo principal
THUMBNAIL_SHORTS_COUNT=2           # 1-3 para shorts
```

---

## 🎯 Exemplos Práticos

### **Primeira vez usando:**
```bash
# 1. Instalar
./instalar.sh

# 2. Configurar APIs
cp _env .env
# Edite .env com suas chaves

# 3. Usar modo interativo
python3 content_pipeline.py
# Escolha opção 1 → INDIVIDUAL
```

### **Processar um vídeo rapidamente:**
```bash
python3 content_pipeline.py --complete "videos/aula.mp4" 1 1
```

### **Adicionar funcionalidades YouTube:**
```bash
python3 content_pipeline.py --youtube modulo-01/aula-01-exemplo
# Configure legendas, capítulos, shorts, metadados, thumbnails
```

### **Processar todos os vídeos:**
```bash
python3 content_pipeline.py --batch
```

---

## 🛠️ Solução de Problemas

### ❌ **"Dependências não encontradas"**
```bash
./instalar.sh
```

### ❌ **"GROQ_API_KEY não encontrada"**
```bash
# Verifique se o .env existe e tem a chave correta
cat .env | grep GROQ_API_KEY
```

### ❌ **"FFmpeg não encontrado"**
```bash
# Verifique se está no diretório bin/
ls -la bin/ffmpeg
```

### ❌ **"Nenhum vídeo encontrado"**
```bash
# Coloque vídeos na pasta videos/
# Formatos: mp4, avi, mov, mkv, webm, m4v
```

### 🐛 **Modo Debug**
```bash
# Ative debug no .env
DEBUG_MODE=true
SAVE_DEBUG_FILES=true

# Logs salvos em temp/debug/
```

---

## 💰 Custos Estimados

- **Groq (Transcrição):** ~$0.27 por hora de áudio
- **Gemini (Análise):** ~$0.075 por 1M tokens (Flash)
- **Thumbnails:** Depende do modelo escolhido

---

## 📚 Estrutura do Curso

### 📁 Módulo 01
**🎥 [Aula 01 - Introdução ao N8N e Automação com IA](./modulo-01/aula-01-introducao-n8n/)**
- Conceitos fundamentais do N8N
- Arquitetura de agentes de IA
- Diferença entre single agent e multi-agentes

**🎥 [Aula 02 - Instalação Profissional do N8N em VPS](./modulo-01/aula-02-instalacao-n8n/)**
- Setup completo em ambiente de produção
- Docker, Docker Swarm e orquestração
- Configuração de Traefik e Portainer

**🎥 [Aula 03 - Nodes do N8N e Desenvolvimento](./modulo-01/aula-03-nodes-n8n/)**
- Tipos de nodes e triggers
- Node Code (JavaScript/Python)
- Limitações cloud vs self-hosted

---

## 🛠️ Stack Tecnológica

- **N8N** - Ferramenta de automação low-code
- **Docker** - Containerização e orquestração
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e filas
- **Traefik** - Load balancer e proxy reverso
- **Portainer** - Interface de gerenciamento Docker
- **Notion** - Integração para produtividade
- **Cloudflare** - DNS e SSL

---

## 💡 Dicas Importantes

1. **Use o modo interativo** - É o mais fácil e guiado
2. **Coloque vídeos na pasta `videos/`** antes de executar
3. **Configure as APIs** na primeira execução
4. **Teste com um vídeo** antes de processar muitos
5. **Use funcionalidades YouTube** conforme sua necessidade

---

## 🎉 Resultado Final

Após o processamento, você terá:
- 📄 **README.md** - Documentação completa da aula
- 📊 **transcricao.json** - Texto transcrito com timestamps
- 🧠 **analise.json** - Análise inteligente do conteúdo
- 💻 **scripts/** - Comandos e códigos extraídos
- 🎬 **Funcionalidades YouTube** (se habilitadas)

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique o status do sistema: `python3 content_pipeline.py` → Opção 5
2. Consulte os logs de erro
3. Verifique as variáveis de ambiente
4. Teste com funcionalidades individuais primeiro

---

**⭐ Sistema Unificado v3.0.0 - Full Stack Club**

*Transformando videoaulas em conhecimento estruturado e conteúdo YouTube pronto!*