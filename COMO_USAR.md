# 🤖 Sistema de Transcrição Inteligente - Guia Rápido

## 🚀 Como Usar (Super Fácil!)

### 1️⃣ **Primeira Instalação**
```bash
# Execute apenas uma vez
./instalar.sh
```

### 2️⃣ **Usando o Sistema (3 Formas)**

#### 🎯 **MODO FÁCIL** (Recomendado para iniciantes)
```bash
./interactive.sh
```
- ✅ Interface guiada passo a passo
- ✅ Configuração automática das APIs
- ✅ Seleção visual de vídeos
- ✅ Modo totalmente interativo

#### ⚡ **MODO RÁPIDO** (Para usuários experientes)
```bash
# Processar um vídeo específico
./run.sh --complete "videos/meu_video.mp4" 1 1

# Processar todos os vídeos
./run.sh --batch

# Apenas transcrever (sem análise)
./run.sh "videos/meu_video.mp4"
```

#### 🔧 **MODO AVANÇADO** (Controle total)
```bash
# Ativar ambiente manualmente
source ativar.sh

# Usar comandos Python diretos
python transcribe.py --complete "videos/video.mp4" 1 1
python transcribe.py --batch
```

## 📋 **Configuração das APIs**

### 🔑 **Groq API (Obrigatória)**
1. Acesse: https://console.groq.com/
2. Crie uma conta gratuita
3. Gere uma API Key
4. Execute `./interactive.sh` e cole a chave quando solicitado

### 🧠 **Gemini API (Opcional)**
1. Acesse: https://ai.google.dev/
2. Faça login com conta Google
3. Clique em "Get API Key"
4. Execute `./interactive.sh` e configure quando solicitado

## 📁 **Estrutura de Arquivos**

```
📦 Projeto
├── 🎬 videos/                    # Coloque seus vídeos aqui
├── 📚 modulo-01/                 # Aulas processadas
│   └── aula-01-nome-da-aula/
│       ├── README.md             # Documentação completa
│       ├── transcricao.json      # Texto transcrito
│       ├── analise.json          # Análise estruturada
│       └── scripts/              # Comandos extraídos
├── 🔧 temp/                      # Arquivos temporários
├── 🚀 interactive.sh             # Modo fácil
├── ⚡ run.sh                     # Modo rápido
├── 🔑 .env                       # Suas chaves de API
└── 📖 COMO_USAR.md              # Este arquivo
```

## 🎯 **Exemplos Práticos**

### Primeira vez usando:
```bash
./interactive.sh
```

### Processar um vídeo rapidamente:
```bash
./run.sh --complete "videos/Dashboard Chatwoot - Timeline Unificado de Conversas.mp4" 2 1
```

### Processar vários vídeos:
```bash
./run.sh --batch
```

## 🆘 **Problemas Comuns**

### ❌ "Groq não instalado"
**Solução:** O ambiente virtual não está ativado
```bash
# Use sempre os scripts facilitados:
./interactive.sh    # ou
./run.sh --complete video.mp4 1 1
```

### ❌ "GROQ_API_KEY não configurada"
**Solução:** Configure a chave da API
```bash
./interactive.sh  # Vai te ajudar a configurar
```

### ❌ "Nenhum vídeo encontrado"
**Solução:** Coloque vídeos na pasta `videos/`
```bash
# Formatos suportados: mp4, avi, mov, mkv, webm, m4v
cp /caminho/para/video.mp4 videos/
./interactive.sh
```

## 💡 **Dicas Importantes**

1. **Use o `./interactive.sh`** - É o modo mais fácil!
2. **Coloque vídeos na pasta `videos/`** antes de executar
3. **Configure as APIs** na primeira execução
4. **Nunca execute** `python transcribe.py` diretamente
5. **Use sempre** os scripts `interactive.sh` ou `run.sh`

## 🎉 **Resultado Final**

Após o processamento, você terá:
- 📄 **README.md** - Documentação completa da aula
- 📊 **transcricao.json** - Texto transcrito com timestamps
- 🧠 **analise.json** - Análise inteligente do conteúdo
- 💻 **scripts/** - Comandos e códigos extraídos

---

## 🚀 **Inicio Rápido (TL;DR)**

```bash
# 1. Instalar (apenas uma vez)
./instalar.sh

# 2. Colocar vídeos na pasta videos/

# 3. Executar modo fácil
./interactive.sh

# 4. Seguir as instruções na tela
```

**Pronto! Seu sistema está funcionando! 🎉** 