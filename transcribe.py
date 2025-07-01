#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Avançado de Transcrição e Análise de Vídeos Educacionais
Mantém 100% de compatibilidade com o sistema original transcribe.py
Adiciona funcionalidades inteligentes de análise e organização

Autor: Sistema Full Stack Club
Versão: 2.0.0
"""

import os
import sys
import json
import subprocess
import math
import time
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Importações condicionais para não quebrar o sistema se não tiver as dependências
try:
    from google import genai
    from google.genai import types
    from pydantic import BaseModel, Field
    from typing import List, Dict, Optional
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  Google Gemini não instalado. Funcionalidades de análise desabilitadas.")
    print("   Para instalar: pip install google-genai pydantic")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("❌ Groq não instalado. Sistema de transcrição não funcionará.")
    sys.exit(1)

# --- CONFIGURAÇÕES DINÂMICAS ---
# Todas as configurações podem ser alteradas via variáveis de ambiente

# Configurações de Transcrição
CHUNK_DURATION_SECONDS = int(os.environ.get("CHUNK_SIZE_SECONDS", "600"))  # 10 minutos padrão
GROQ_MODEL = os.environ.get("GROQ_MODEL", "whisper-large-v3-turbo")
GROQ_LANGUAGE = os.environ.get("GROQ_LANGUAGE", "pt")

# Configurações de Sistema
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "300"))  # 5 minutos
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"
SAVE_DEBUG_FILES = os.environ.get("SAVE_DEBUG_FILES", "false").lower() == "true"

# Caminhos de Sistema
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "./bin/ffmpeg")
FFPROBE_PATH = os.environ.get("FFPROBE_PATH", "./bin/ffprobe")
TEMP_DIR = os.environ.get("TEMP_DIR_NAME", "temp")
OUTPUT_BASE_DIR = os.environ.get("OUTPUT_BASE_DIR", "modulo-{modulo:02d}")
VIDEOS_DIR = os.environ.get("VIDEOS_DIR", "videos")

# Configurações de Áudio
AUDIO_SAMPLE_RATE = int(os.environ.get("AUDIO_SAMPLE_RATE", "16000"))
AUDIO_CHANNELS = int(os.environ.get("AUDIO_CHANNELS", "1"))
AUDIO_FORMAT = os.environ.get("AUDIO_FORMAT", "flac")

# Padrões de Diretório
AULA_DIR_PATTERN = os.environ.get("AULA_DIR_PATTERN", "aula-{numero:02d}-{slug}")

@dataclass
class TranscriptionResult:
    """Resultado da transcrição"""
    text: str
    segments: List[Dict]
    words: List[Dict]
    duration: float
    metadata: Dict[str, Any]

# --- MODELOS PYDANTIC PARA STRUCTURED OUTPUT ---
if GEMINI_AVAILABLE:
    class Conceito(BaseModel):
        conceito: str = Field(description="Nome do conceito técnico")
        definicao: str = Field(description="Explicação clara e concisa do conceito")

    class AnalysisSchema(BaseModel):
        titulo_sugerido: str = Field(description="Título descritivo e profissional da aula")
        resumo_executivo: str = Field(description="Resumo conciso em 2-3 parágrafos sobre o conteúdo principal")
        pontos_chave: List[str] = Field(description="Lista de 3-5 pontos mais importantes da aula", min_items=3, max_items=5)
        tecnologias_mencionadas: List[str] = Field(description="Tecnologias, frameworks, ferramentas mencionadas")
        comandos_codigo: List[str] = Field(description="Comandos de terminal, código ou scripts mencionados")
        conceitos_importantes: List[Conceito] = Field(description="Conceitos técnicos importantes explicados na aula")
        nivel_dificuldade: str = Field(description="Nível de dificuldade: básico, intermediário ou avançado")
        duracao_estimada: str = Field(description="Duração estimada da aula em minutos")
        pre_requisitos: List[str] = Field(description="Conhecimentos prévios necessários")
        objetivos_aprendizado: List[str] = Field(description="O que o aluno aprenderá ao final da aula")
        tags: List[str] = Field(description="Tags relevantes para categorização e busca")
        
        class Config:
            title = "Análise de Aula Técnica"
            description = "Estrutura completa de análise de conteúdo educacional técnico"

@dataclass
class AnalysisResult:
    """Resultado da análise (compatibilidade com código existente)"""
    titulo_sugerido: str
    resumo_executivo: str
    pontos_chave: List[str]
    tecnologias_mencionadas: List[str]
    comandos_codigo: List[str]
    conceitos_importantes: List[Dict[str, str]]
    nivel_dificuldade: str
    duracao_estimada: str
    pre_requisitos: List[str]
    objetivos_aprendizado: List[str]
    tags: List[str]

# --- FUNÇÕES DE DEBUG ---

def debug_print(message: str):
    """Print debug se modo debug estiver ativo"""
    if DEBUG_MODE:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"🐛 [{timestamp}] {message}")

def save_debug_file(content: Any, filename: str):
    """Salva arquivo de debug se habilitado"""
    if SAVE_DEBUG_FILES:
        debug_dir = os.path.join(TEMP_DIR, "debug")
        os.makedirs(debug_dir, exist_ok=True)
        debug_path = os.path.join(debug_dir, filename)
        
        if isinstance(content, (dict, list)):
            with open(debug_path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
        else:
            with open(debug_path, "w", encoding="utf-8") as f:
                f.write(str(content))
        
        debug_print(f"Debug file saved: {debug_path}")

# --- FUNÇÕES ORIGINAIS MANTIDAS ---

def get_audio_duration(file_path: str) -> Optional[float]:
    """
    Obtém a duração de um arquivo de mídia usando ffprobe.
    FUNÇÃO ORIGINAL MANTIDA INTACTA COM CONFIGURAÇÕES DINÂMICAS
    """
    command = [
        FFPROBE_PATH,
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        file_path
    ]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=REQUEST_TIMEOUT)
        duration = float(result.stdout)
        debug_print(f"Audio duration: {duration:.2f}s for {file_path}")
        return duration
    except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired) as e:
        print(f"Erro ao obter a duração do áudio de {file_path}: {e}")
        return None

def transcribe_video_original(video_path: str) -> Optional[Dict[str, Any]]:
    """
    FUNÇÃO ORIGINAL DE TRANSCRIÇÃO MANTIDA 100% INTACTA COM CONFIGURAÇÕES DINÂMICAS
    Transcreve um arquivo de vídeo usando a API Groq, dividindo o áudio em pedaços (chunks) se necessário.
    """
    print(f"Iniciando o processo para: {video_path}")
    debug_print(f"Configurações: CHUNK_SIZE={CHUNK_DURATION_SECONDS}s, MODEL={GROQ_MODEL}, LANG={GROQ_LANGUAGE}")

    # 1. Validar API Key
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Erro: A variável de ambiente GROQ_API_KEY não foi encontrada.")
        return None
    client = Groq(api_key=api_key)

    # 2. Preparar caminhos
    base_name = os.path.basename(video_path)
    file_name, _ = os.path.splitext(base_name)
    temp_dir = TEMP_DIR
    os.makedirs(temp_dir, exist_ok=True)
    final_transcription_path = os.path.join(temp_dir, f"{file_name}_transcription.json")

    # 3. Obter duração e calcular chunks
    duration = get_audio_duration(video_path)
    if duration is None:
        return None
    
    num_chunks = math.ceil(duration / CHUNK_DURATION_SECONDS)
    print(f"Duração do vídeo: {duration:.2f}s. Dividindo em {num_chunks} pedaço(s).")

    all_segments = []
    total_words = []
    transcribed_duration = 0.0

    for i in range(num_chunks):
        chunk_num = i + 1
        start_time = i * CHUNK_DURATION_SECONDS
        chunk_audio_path = os.path.join(temp_dir, f"{file_name}_chunk_{chunk_num}.{AUDIO_FORMAT}")
        
        print(f"\n--- Processando Pedaço {chunk_num}/{num_chunks} ---")
        print(f"Convertendo áudio (início: {start_time}s)...")

        # 4. Converter um pedaço do vídeo para áudio com configurações dinâmicas
        ffmpeg_command = [
            FFMPEG_PATH,
            "-i", video_path,
            "-ss", str(start_time),
            "-t", str(CHUNK_DURATION_SECONDS),
            "-vn", 
            "-ar", str(AUDIO_SAMPLE_RATE), 
            "-ac", str(AUDIO_CHANNELS), 
            "-c:a", AUDIO_FORMAT,
            "-y", chunk_audio_path
        ]
        
        debug_print(f"FFmpeg command: {' '.join(ffmpeg_command)}")
        
        try:
            result = subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True, timeout=REQUEST_TIMEOUT)
            debug_print(f"FFmpeg success for chunk {chunk_num}")
            if SAVE_DEBUG_FILES:
                save_debug_file(result.stderr, f"ffmpeg_chunk_{chunk_num}_output.log")
        except subprocess.CalledProcessError as e:
            print(f"Erro no ffmpeg para o pedaço {chunk_num}: {e.stderr}")
            save_debug_file(str(e), f"ffmpeg_chunk_{chunk_num}_error.log")
            continue # Pula para o próximo pedaço
        except subprocess.TimeoutExpired:
            print(f"Timeout no ffmpeg para o pedaço {chunk_num}")
            continue

        # 5. Transcrever o pedaço com a API
        print(f"Enviando pedaço {chunk_num} para a API do Groq...")
        
        retry_count = 0
        transcription = None
        
        while retry_count < MAX_RETRIES and transcription is None:
            try:
                with open(chunk_audio_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(os.path.basename(chunk_audio_path), file.read()),
                        model=GROQ_MODEL,
                        response_format="verbose_json",
                        timestamp_granularities=["word", "segment"],
                        language=GROQ_LANGUAGE
                    ).to_dict()

                # Acumular resultados, ajustando timestamps
                for segment in transcription.get('segments', []):
                    segment['start'] += start_time
                    segment['end'] += start_time
                    all_segments.append(segment)
                
                for word in transcription.get('words', []):
                    word['start'] += start_time
                    word['end'] += start_time
                    total_words.append(word)

                chunk_transcribed_duration = transcription.get('duration', 0)
                transcribed_duration += chunk_transcribed_duration
                print(f"Pedaço {chunk_num} transcrito com sucesso.")
                
                # Salvar debug da transcrição
                if SAVE_DEBUG_FILES:
                    save_debug_file(transcription, f"transcription_chunk_{chunk_num}.json")

            except Exception as e:
                retry_count += 1
                print(f"Erro na transcrição do pedaço {chunk_num} (tentativa {retry_count}/{MAX_RETRIES}): {e}")
                save_debug_file(str(e), f"transcription_chunk_{chunk_num}_error_{retry_count}.log")
                
                if retry_count < MAX_RETRIES:
                    wait_time = 2 ** retry_count  # Backoff exponencial
                    print(f"Aguardando {wait_time}s antes da próxima tentativa...")
                    time.sleep(wait_time)
        
        # Limpar arquivo temporário após tentativas (a menos que esteja em modo debug)
        if os.path.exists(chunk_audio_path) and not SAVE_DEBUG_FILES:
            os.remove(chunk_audio_path)
        elif SAVE_DEBUG_FILES:
            debug_print(f"Chunk file preserved for debug: {chunk_audio_path}")

    # 6. Montar o JSON final
    full_text = " ".join([word['word'] for word in total_words])
    final_result = {
        "text": full_text.strip(),
        "segments": all_segments,
        "words": total_words,
        "duration": transcribed_duration,
        "metadata": {
            "original_file": video_path,
            "chunks_processed": num_chunks,
            "model_used": GROQ_MODEL,
            "language": GROQ_LANGUAGE,
            "chunk_size_seconds": CHUNK_DURATION_SECONDS,
            "processed_at": datetime.now().isoformat()
        }
    }

    with open(final_transcription_path, "w", encoding="utf-8") as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)

    print(f"\n--- Processo Concluído ---")
    print(f"Transcrição final combinada e salva em: {final_transcription_path}")
    
    debug_print(f"Final stats: {len(total_words)} words, {len(all_segments)} segments, {transcribed_duration:.2f}s")
    
    return final_result

# --- NOVAS FUNCIONALIDADES ENHANCED ---

class EnhancedTranscriptionSystem:
    """Sistema avançado de transcrição e análise de conteúdo educacional"""
    
    def __init__(self):
        self.setup_apis()
        # Não criar diretórios automaticamente - apenas quando processar vídeos
        
    def setup_apis(self):
        """Configura as APIs necessárias"""
        # Groq para transcrição
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        if not self.groq_api_key:
            print("❌ GROQ_API_KEY não encontrada")
            self.groq_available = False
        else:
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                self.groq_available = True
                print("✅ Groq configurado")
            except Exception as e:
                print(f"❌ Erro ao configurar Groq: {e}")
                self.groq_available = False
        
        # Gemini para análise (opcional)
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not self.gemini_api_key or not GEMINI_AVAILABLE:
            print("⚠️  GEMINI_API_KEY não encontrada ou biblioteca não instalada")
            print("   Funcionalidades de análise inteligente desabilitadas")
            self.gemini_available = False
        else:
            try:
                # Configurar cliente Gemini com nova API
                self.gemini_client = genai.Client(api_key=self.gemini_api_key)
                
                # Configurações opcionais do ambiente
                self.gemini_model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
                self.thinking_enabled = os.environ.get("GEMINI_THINKING", "true").lower() == "true"
                self.thinking_budget = int(os.environ.get("GEMINI_THINKING_BUDGET", "-1"))  # -1 = dinâmico
                self.max_context = int(os.environ.get("GEMINI_MAX_CONTEXT", "1000000"))  # 1M tokens por padrão
                
                print(f"✅ Gemini configurado: {self.gemini_model}")
                if self.thinking_enabled:
                    print(f"🧠 Thinking habilitado (budget: {self.thinking_budget})")
                else:
                    print("⚡ Thinking desabilitado para performance")
                print(f"📄 Contexto máximo: {self.max_context:,} tokens")
                
                self.gemini_available = True
            except Exception as e:
                print(f"❌ Erro ao configurar Gemini: {e}")
                self.gemini_available = False
        
    def ensure_directories(self):
        """Garante que os diretórios necessários existam"""
        os.makedirs(TEMP_DIR, exist_ok=True)
        os.makedirs("videos", exist_ok=True)
        
    def transcribe_video(self, video_path: str) -> Optional[TranscriptionResult]:
        """
        Transcreve vídeo usando a função original
        """
        if not self.groq_available:
            print("❌ Groq não disponível. Não é possível transcrever.")
            return None
            
        result = transcribe_video_original(video_path)
        if not result:
            return None
            
        # Converter para TranscriptionResult
        base_name = os.path.basename(video_path)
        file_name, _ = os.path.splitext(base_name)
        
        return TranscriptionResult(
            text=result["text"],
            segments=result["segments"],
            words=result["words"],
            duration=result["duration"],
            metadata={
                "file_name": file_name,
                "original_path": video_path,
                "transcription_date": datetime.now().isoformat(),
                "chunks_processed": math.ceil(result["duration"] / CHUNK_DURATION_SECONDS)
            }
        )

    def analyze_content_with_gemini(self, transcription: TranscriptionResult) -> Optional[AnalysisResult]:
        """Analisa conteúdo transcrito usando Gemini com structured output e thinking"""
        if not self.gemini_available:
            print("⚠️  Gemini não disponível. Usando análise básica.")
            return self._basic_analysis(transcription)
            
        # Aproveitar o contexto longo do Gemini (até 1M+ tokens)
        # Calcular tokens aproximados (1 token ≈ 4 caracteres em português)
        estimated_tokens = len(transcription.text) // 4
        
        if estimated_tokens > self.max_context:
            # Se exceder, usar estratégia inteligente de truncamento
            # Manter início e final, resumir meio
            text_start = transcription.text[:self.max_context//3 * 4]
            text_end = transcription.text[-self.max_context//3 * 4:]
            text_sample = f"{text_start}\n\n[... CONTEÚDO INTERMEDIÁRIO OMITIDO ...]\n\n{text_end}"
            print(f"📊 Texto truncado: {estimated_tokens:,} → {self.max_context:,} tokens")
        else:
            text_sample = transcription.text
            print(f"📊 Processando {estimated_tokens:,} tokens de contexto")

        # System instruction otimizada para análise educacional
        system_instruction = """Você é um especialista em análise de conteúdo educacional técnico. 
        Sua função é extrair informações estruturadas de transcrições de aulas técnicas, 
        identificando conceitos, tecnologias, comandos e organizando o conhecimento de forma didática.
        
        Seja preciso, técnico e educativo. Extraia apenas informações que estão explicitamente 
        presentes na transcrição. Mantenha consistência terminológica."""

        # Prompt otimizado para thinking e long context
        analysis_prompt = f"""Analise esta transcrição de aula técnica em português e extraia informações estruturadas:

CONTEXTO DA AULA:
- Duração da gravação: {transcription.duration/60:.1f} minutos
- Palavras transcritas: {len(transcription.words):,}
- Segmentos de áudio: {len(transcription.segments)}

TRANSCRIÇÃO COMPLETA:
{text_sample}

INSTRUÇÕES PARA ANÁLISE:
1. Leia toda a transcrição com atenção
2. Identifique o tema principal e subtemas
3. Extraia tecnologias, ferramentas e frameworks mencionados
4. Capture comandos de código, terminal ou configurações
5. Identifique conceitos técnicos explicados e suas definições
6. Determine o nível de dificuldade baseado na complexidade dos conceitos
7. Sugira pré-requisitos baseado nas tecnologias e conceitos apresentados
8. Defina objetivos de aprendizado específicos e mensuráveis

Seja detalhado na análise e precise nas informações extraídas."""

        try:
            print("🧠 Iniciando análise inteligente com Gemini...")
            
            # Configurar thinking se habilitado
            thinking_config = None
            if self.thinking_enabled:
                try:
                    thinking_config = types.GenerationConfigThinkingConfig(
                        thinking_budget=self.thinking_budget if self.thinking_budget != -1 else None,
                        include_thoughts=False  # Não incluir thoughts na resposta para economizar tokens
                    )
                    print(f"🧠 Using thinking with budget: {self.thinking_budget}")
                except AttributeError:
                    print("⚠️  Thinking não disponível nesta versão do SDK")
                    thinking_config = None
            
            # Configuração de geração com structured output
            generation_config_params = {
                "response_mime_type": "application/json",
                "response_schema": AnalysisSchema,
                "temperature": 0.1,  # Baixa temperatura para consistência
                "system_instruction": system_instruction,
            }
            
            # Adicionar thinking config se disponível
            if thinking_config:
                generation_config_params["thinking_config"] = thinking_config
            
            # Fazer a chamada para o Gemini
            response = self.gemini_client.models.generate_content(
                model=self.gemini_model,
                contents=analysis_prompt,
                config=types.GenerateContentConfig(**generation_config_params)
            )
            
            # Usar structured output direto (response.parsed)
            if hasattr(response, 'parsed') and response.parsed:
                analysis_data = response.parsed
                print("✅ Structured output recebido com sucesso")
            else:
                # Fallback para parsing manual se structured output falhar
                print("⚠️  Fallback para parsing manual")
                response_text = response.text.strip()
                analysis_data = json.loads(response_text)
            
            # Converter conceitos para formato compatível
            conceitos_convertidos = []
            if hasattr(analysis_data, 'conceitos_importantes'):
                for conceito in analysis_data.conceitos_importantes:
                    if hasattr(conceito, 'conceito') and hasattr(conceito, 'definicao'):
                        conceitos_convertidos.append({
                            "conceito": conceito.conceito,
                            "definicao": conceito.definicao
                        })
            elif isinstance(analysis_data, dict) and 'conceitos_importantes' in analysis_data:
                conceitos_convertidos = analysis_data['conceitos_importantes']
            
            # Converter para AnalysisResult (compatibilidade)
            if hasattr(analysis_data, 'titulo_sugerido'):
                # Objeto Pydantic
                analysis = AnalysisResult(
                    titulo_sugerido=analysis_data.titulo_sugerido,
                    resumo_executivo=analysis_data.resumo_executivo,
                    pontos_chave=analysis_data.pontos_chave,
                    tecnologias_mencionadas=analysis_data.tecnologias_mencionadas,
                    comandos_codigo=analysis_data.comandos_codigo,
                    conceitos_importantes=conceitos_convertidos,
                    nivel_dificuldade=analysis_data.nivel_dificuldade,
                    duracao_estimada=analysis_data.duracao_estimada,
                    pre_requisitos=analysis_data.pre_requisitos,
                    objetivos_aprendizado=analysis_data.objetivos_aprendizado,
                    tags=analysis_data.tags
                )
            else:
                # Dict normal
                analysis = AnalysisResult(
                    titulo_sugerido=analysis_data.get("titulo_sugerido", "Aula Técnica"),
                    resumo_executivo=analysis_data.get("resumo_executivo", ""),
                    pontos_chave=analysis_data.get("pontos_chave", []),
                    tecnologias_mencionadas=analysis_data.get("tecnologias_mencionadas", []),
                    comandos_codigo=analysis_data.get("comandos_codigo", []),
                    conceitos_importantes=conceitos_convertidos,
                    nivel_dificuldade=analysis_data.get("nivel_dificuldade", "intermediário"),
                    duracao_estimada=analysis_data.get("duracao_estimada", f"{int(transcription.duration//60)} minutos"),
                    pre_requisitos=analysis_data.get("pre_requisitos", []),
                    objetivos_aprendizado=analysis_data.get("objetivos_aprendizado", []),
                    tags=analysis_data.get("tags", [])
                )
            
            # Mostrar estatísticas do uso
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                print(f"📊 Tokens utilizados:")
                print(f"   • Input: {usage.prompt_token_count:,}")
                print(f"   • Output: {usage.candidates_token_count:,}")
                if hasattr(usage, 'thoughts_token_count') and usage.thoughts_token_count:
                    print(f"   • Thinking: {usage.thoughts_token_count:,}")
                print(f"   • Total: {usage.total_token_count:,}")
            
            print("✅ Análise inteligente concluída com sucesso")
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise Gemini: {e}")
            print("🔄 Tentando análise básica como fallback...")
            return self._basic_analysis(transcription)

    def _basic_analysis(self, transcription: TranscriptionResult) -> AnalysisResult:
        """Análise básica quando Gemini não está disponível"""
        file_name = transcription.metadata.get("file_name", "Aula")
        
        # Extrair algumas informações básicas do texto
        text = transcription.text.lower()
        
        # Detectar tecnologias comuns
        tech_keywords = {
            "docker": "Docker",
            "n8n": "N8N", 
            "postgres": "PostgreSQL",
            "redis": "Redis",
            "traefik": "Traefik",
            "portainer": "Portainer",
            "javascript": "JavaScript",
            "python": "Python",
            "nodejs": "Node.js",
            "react": "React",
            "vue": "Vue.js",
            "api": "API",
            "webhook": "Webhook",
            "json": "JSON",
            "sql": "SQL",
            "html": "HTML",
            "css": "CSS"
        }
        
        detected_techs = []
        for keyword, tech_name in tech_keywords.items():
            if keyword in text:
                detected_techs.append(tech_name)
        
        # Detectar comandos básicos
        command_patterns = [
            r'docker\s+\w+',
            r'npm\s+\w+',
            r'pip\s+\w+',
            r'git\s+\w+',
            r'sudo\s+\w+',
            r'chmod\s+\d+',
            r'mkdir\s+\w+',
            r'cd\s+\w+'
        ]
        
        detected_commands = []
        for pattern in command_patterns:
            matches = re.findall(pattern, text)
            detected_commands.extend(matches[:3])  # Limitar a 3 por padrão
        
        return AnalysisResult(
            titulo_sugerido=f"Aula - {file_name}",
            resumo_executivo=f"Esta aula aborda conteúdo técnico relacionado a {', '.join(detected_techs[:3]) if detected_techs else 'desenvolvimento'}. O conteúdo tem duração de aproximadamente {int(transcription.duration//60)} minutos e apresenta conceitos práticos e teóricos importantes para o aprendizado.",
            pontos_chave=["Conteúdo técnico prático", "Conceitos fundamentais", "Exemplos aplicados"],
            tecnologias_mencionadas=detected_techs[:5],
            comandos_codigo=detected_commands[:5],
            conceitos_importantes=[],
            nivel_dificuldade="intermediário",
            duracao_estimada=f"{int(transcription.duration//60)} minutos",
            pre_requisitos=["Conhecimento básico de programação"],
            objetivos_aprendizado=["Compreender os conceitos apresentados", "Aplicar conhecimentos práticos"],
            tags=["aula", "técnico", "programação"] + detected_techs[:2]
        )

    def create_slug(self, title: str) -> str:
        """Cria slug limpo a partir do título"""
        # Remover "Aula - " do início se existir
        title = re.sub(r'^aula\s*-\s*', '', title, flags=re.IGNORECASE)
        
        # Substituir acentos
        replacements = {
            'à': 'a', 'á': 'a', 'â': 'a', 'ã': 'a', 'ä': 'a',
            'è': 'e', 'é': 'e', 'ê': 'e', 'ë': 'e',
            'ì': 'i', 'í': 'i', 'î': 'i', 'ï': 'i',
            'ò': 'o', 'ó': 'o', 'ô': 'o', 'õ': 'o', 'ö': 'o',
            'ù': 'u', 'ú': 'u', 'û': 'u', 'ü': 'u',
            'ç': 'c', 'ñ': 'n'
        }
        
        slug = title.lower()
        for char, replacement in replacements.items():
            slug = slug.replace(char, replacement)
        
        # Remover caracteres especiais e normalizar
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'\s+', '-', slug)
        slug = re.sub(r'-+', '-', slug)
        slug = slug.strip('-')
        
        return slug[:50]  # Limitar tamanho

    def generate_directory_structure(self, analysis: AnalysisResult, modulo: int, aula: int) -> str:
        """Gera estrutura de diretórios para a aula"""
        slug = self.create_slug(analysis.titulo_sugerido)
        
        modulo_dir = OUTPUT_BASE_DIR.format(modulo=modulo)
        aula_dir = os.path.join(modulo_dir, AULA_DIR_PATTERN.format(numero=aula, slug=slug))
        
        # Criar diretórios
        os.makedirs(aula_dir, exist_ok=True)
        os.makedirs(os.path.join(aula_dir, "assets"), exist_ok=True)
        os.makedirs(os.path.join(aula_dir, "scripts"), exist_ok=True)
        
        return aula_dir

    def generate_readme_content(self, analysis: AnalysisResult, transcription: TranscriptionResult) -> str:
        """Gera conteúdo do README.md"""
        
        # Pontos-chave formatados
        pontos_chave_text = "\n".join([f"• **{ponto}**" for ponto in analysis.pontos_chave])
        
        # Tecnologias formatadas
        tecnologias_text = "\n".join([f"• **{tech}**" for tech in analysis.tecnologias_mencionadas])
        
        # Comandos formatados
        comandos_text = ""
        if analysis.comandos_codigo:
            comandos_text = "\n## 💻 Comandos Utilizados\n\n```bash\n" + "\n".join(analysis.comandos_codigo) + "\n```\n"
        
        # Conceitos importantes formatados
        conceitos_text = ""
        if analysis.conceitos_importantes:
            conceitos_text = "\n## 💡 Conceitos Importantes\n\n"
            for conceito in analysis.conceitos_importantes:
                conceitos_text += f"**{conceito['conceito']}**: {conceito['definicao']}\n\n"
        
        # Pré-requisitos formatados
        pre_requisitos_text = ""
        if analysis.pre_requisitos:
            pre_requisitos_text = "\n## 📋 Pré-requisitos\n\n" + "\n".join([f"• {req}" for req in analysis.pre_requisitos]) + "\n"
        
        # Objetivos de aprendizado formatados
        objetivos_text = ""
        if analysis.objetivos_aprendizado:
            objetivos_text = "\n## 🎯 Objetivos de Aprendizado\n\n" + "\n".join([f"• {obj}" for obj in analysis.objetivos_aprendizado]) + "\n"
        
        readme_content = f"""# {analysis.titulo_sugerido}

{analysis.resumo_executivo}

## 📚 Pontos-Chave

{pontos_chave_text}

## 🛠️ Tecnologias Mencionadas

{tecnologias_text}
{comandos_text}
{conceitos_text}
{pre_requisitos_text}
{objetivos_text}
## ⏱️ Duração
{analysis.duracao_estimada}

## 📊 Informações Técnicas
- **Nível de Dificuldade**: {analysis.nivel_dificuldade.title()}
- **Palavras Transcritas**: {len(transcription.words):,}
- **Segmentos de Áudio**: {len(transcription.segments)}
- **Duração Real**: {transcription.duration/60:.1f} minutos

## 🏷️ Tags
{', '.join([f'`{tag}`' for tag in analysis.tags])}

<details>
<summary>📝 Transcrição Completa</summary>

{transcription.text}

</details>
"""
        
        return readme_content

    def save_analysis_files(self, transcription: TranscriptionResult, analysis: AnalysisResult, output_dir: str) -> List[str]:
        """Salva todos os arquivos da análise"""
        files_created = []
        
        try:
            # 1. Salvar transcrição JSON
            transcription_path = os.path.join(output_dir, "transcricao.json")
            transcription_data = {
                "text": transcription.text,
                "segments": transcription.segments,
                "words": transcription.words,
                "duration": transcription.duration,
                "metadata": transcription.metadata
            }
            with open(transcription_path, "w", encoding="utf-8") as f:
                json.dump(transcription_data, f, ensure_ascii=False, indent=2)
            files_created.append(transcription_path)
            print(f"✅ Transcrição salva: {transcription_path}")
            
            # 2. Salvar análise JSON
            analysis_path = os.path.join(output_dir, "analise.json")
            analysis_data = {
                "titulo_sugerido": analysis.titulo_sugerido,
                "resumo_executivo": analysis.resumo_executivo,
                "pontos_chave": analysis.pontos_chave,
                "tecnologias_mencionadas": analysis.tecnologias_mencionadas,
                "comandos_codigo": analysis.comandos_codigo,
                "conceitos_importantes": analysis.conceitos_importantes,
                "nivel_dificuldade": analysis.nivel_dificuldade,
                "duracao_estimada": analysis.duracao_estimada,
                "pre_requisitos": analysis.pre_requisitos,
                "objetivos_aprendizado": analysis.objetivos_aprendizado,
                "tags": analysis.tags
            }
            with open(analysis_path, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            files_created.append(analysis_path)
            print(f"✅ Análise salva: {analysis_path}")
            
            # 3. Gerar e salvar README
            readme_content = self.generate_readme_content(analysis, transcription)
            readme_path = os.path.join(output_dir, "README.md")
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            files_created.append(readme_path)
            print(f"✅ README gerado: {readme_path}")
            
            # 4. Salvar comandos em arquivo separado se houver
            if analysis.comandos_codigo:
                scripts_dir = os.path.join(output_dir, "scripts")
                commands_file = os.path.join(scripts_dir, "comandos.md")
                with open(commands_file, "w", encoding="utf-8") as f:
                    f.write("# Comandos da Aula\n\n")
                    for i, cmd in enumerate(analysis.comandos_codigo, 1):
                        f.write(f"## Comando {i}\n```bash\n{cmd}\n```\n\n")
                files_created.append(commands_file)
                print(f"✅ Comandos salvos: {commands_file}")
                
        except Exception as e:
            print(f"❌ Erro ao salvar arquivos: {e}")
            
        return files_created

    def process_video_complete(self, video_path: str, modulo: int = 1, aula: int = 1) -> Dict[str, Any]:
        """Processa um vídeo completamente: transcrição + análise + documentação"""
        print(f"\n{'='*60}")
        print(f"🚀 PROCESSAMENTO COMPLETO - {os.path.basename(video_path)}")
        print(f"{'='*60}")
        
        try:
            # 1. Transcrever vídeo
            print("📹 Etapa 1/4: Transcrevendo vídeo...")
            transcription = self.transcribe_video(video_path)
            if not transcription:
                return {"status": "error", "message": "Falha na transcrição"}
            
            # 2. Analisar conteúdo
            print("🧠 Etapa 2/4: Analisando conteúdo...")
            analysis = self.analyze_content_with_gemini(transcription)
            if not analysis:
                return {"status": "error", "message": "Falha na análise"}
            
            # 3. Criar estrutura de diretórios
            print("📁 Etapa 3/4: Criando estrutura...")
            output_dir = self.generate_directory_structure(analysis, modulo, aula)
            
            # 4. Salvar todos os arquivos
            print("💾 Etapa 4/4: Salvando arquivos...")
            files_created = self.save_analysis_files(transcription, analysis, output_dir)
            
            result = {
                "status": "success",
                "output_dir": output_dir,
                "files_created": files_created,
                "analysis": {
                    "titulo": analysis.titulo_sugerido,
                    "nivel": analysis.nivel_dificuldade,
                    "duracao": analysis.duracao_estimada,
                    "tecnologias": len(analysis.tecnologias_mencionadas),
                    "conceitos": len(analysis.conceitos_importantes)
                },
                "transcription_stats": {
                    "duration": transcription.duration,
                    "words": len(transcription.words),
                    "segments": len(transcription.segments)
                }
            }
            
            print(f"\n✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
            print(f"📁 Aula criada em: {output_dir}")
            print(f"📊 Estatísticas:")
            print(f"   • Duração: {transcription.duration/60:.1f} minutos")
            print(f"   • Palavras: {len(transcription.words):,}")
            print(f"   • Tecnologias: {len(analysis.tecnologias_mencionadas)}")
            print(f"   • Conceitos: {len(analysis.conceitos_importantes)}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERRO NO PROCESSAMENTO: {e}")
            return {"status": "error", "message": str(e)}

    def batch_process_videos(self, videos_dir: str = "videos", start_modulo: int = 1) -> List[Dict[str, Any]]:
        """Processa todos os vídeos em lote"""
        print(f"\n{'='*60}")
        print(f"🎬 PROCESSAMENTO EM LOTE - {videos_dir}")
        print(f"{'='*60}")
        
        # Extensões de vídeo suportadas
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v']
        results = []
        
        if not os.path.exists(videos_dir):
            print(f"❌ Diretório {videos_dir} não encontrado")
            return results
            
        # Encontrar todos os vídeos
        video_files = []
        for ext in video_extensions:
            video_files.extend(Path(videos_dir).glob(f"**/*{ext}"))
        
        if not video_files:
            print(f"❌ Nenhum vídeo encontrado em {videos_dir}")
            return results
            
        # Ordenar por nome
        video_files = sorted(video_files)
        
        print(f"📹 Encontrados {len(video_files)} vídeos para processar")
        print("📁 Vídeos encontrados:")
        for i, video in enumerate(video_files, 1):
            print(f"   {i:2d}. {video.name}")
        
        # Processar cada vídeo
        for i, video_path in enumerate(video_files, 1):
            print(f"\n{'='*60}")
            print(f"🎬 VÍDEO {i}/{len(video_files)}: {video_path.name}")
            print(f"{'='*60}")
            
            # Determinar módulo e aula
            modulo = start_modulo
            aula = i
            
            # Tentar extrair números do nome do arquivo
            filename = video_path.stem
            modulo_match = re.search(r'modulo[-_]?(\d+)', filename, re.IGNORECASE)
            aula_match = re.search(r'aula[-_]?(\d+)', filename, re.IGNORECASE)
            
            if modulo_match:
                modulo = int(modulo_match.group(1))
            if aula_match:
                aula = int(aula_match.group(1))
            
            print(f"📊 Processando como: Módulo {modulo}, Aula {aula}")
            
            result = self.process_video_complete(str(video_path), modulo, aula)
            result['video_info'] = {
                'filename': video_path.name,
                'modulo': modulo,
                'aula': aula,
                'index': i
            }
            results.append(result)
            
            # Pequena pausa entre processamentos
            if i < len(video_files):
                print("⏳ Aguardando 3 segundos...")
                time.sleep(3)
        
        # Relatório final
        print(f"\n{'='*60}")
        print(f"📊 RELATÓRIO FINAL - PROCESSAMENTO EM LOTE")
        print(f"{'='*60}")
        
        successful = [r for r in results if r.get("status") == "success"]
        failed = [r for r in results if r.get("status") == "error"]
        
        print(f"✅ Sucessos: {len(successful)}")
        print(f"❌ Falhas: {len(failed)}")
        
        if successful:
            print(f"\n📁 Aulas criadas com sucesso:")
            for result in successful:
                info = result.get('video_info', {})
                print(f"   • {info.get('filename', 'N/A')} → {result.get('output_dir', 'N/A')}")
                
        if failed:
            print(f"\n❌ Vídeos que falharam:")
            for result in failed:
                info = result.get('video_info', {})
                print(f"   • {info.get('filename', 'N/A')}: {result.get('message', 'Erro desconhecido')}")
        
        return results

# --- FUNÇÃO PRINCIPAL ---

def main():
    """Função principal com compatibilidade total"""
    
    # Verificar se é chamada no modo original (transcribe.py compatibility)
    if len(sys.argv) == 2 and not sys.argv[1].startswith('--'):
        # Modo compatibilidade com transcribe.py original
        video_file = sys.argv[1]
        if os.path.exists(video_file):
            print("🔄 Modo compatibilidade - usando função original")
            result = transcribe_video_original(video_file)
            if result:
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print(f"Erro: O arquivo de vídeo não foi encontrado em '{video_file}'")
            sys.exit(1)
    
    # Modo enhanced
    if len(sys.argv) < 2:
        print("""
🤖 Sistema Avançado de Transcrição e Análise de Vídeos Educacionais

MODOS DE USO:

1. MODO LEGADO (compatível com transcribe.py):
   python transcribe.py video.mp4
   
2. MODO COMPLETO (transcrição + análise + documentação):
   python transcribe.py --complete video.mp4 [modulo] [aula]
   
3. MODO LOTE (processar pasta inteira):
   python transcribe.py --batch [pasta_videos] [modulo_inicial]

EXEMPLOS:
   python transcribe.py videos/aula01.mp4              # Modo legado
   python transcribe.py --complete videos/aula01.mp4 1 1    # Modo completo
   python transcribe.py --batch videos 1                     # Lote
   python transcribe.py --batch                              # Lote pasta padrão

VARIÁVEIS DE AMBIENTE:
   GROQ_API_KEY    - Obrigatória para transcrição
   GEMINI_API_KEY  - Opcional para análise inteligente
   
ESTRUTURA DE ARQUIVOS:
   videos/         - Coloque seus vídeos aqui
   modulo-XX/      - Aulas organizadas serão criadas aqui
   temp/           - Arquivos temporários
        """)
        sys.exit(1)
    
    try:
        system = EnhancedTranscriptionSystem()
        
        command = sys.argv[1]
        
        if command == "--batch":
            # Processamento em lote
            videos_dir = sys.argv[2] if len(sys.argv) > 2 else "videos"
            start_modulo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            
            results = system.batch_process_videos(videos_dir, start_modulo)
            
            # Determinar código de saída
            successful = len([r for r in results if r.get("status") == "success"])
            if successful > 0:
                sys.exit(0)
            else:
                sys.exit(1)
                
        elif command == "--complete":
            # Processamento completo individual
            if len(sys.argv) < 3:
                print("❌ Modo completo requer pelo menos o caminho do vídeo")
                sys.exit(1)
                
            video_path = sys.argv[2]
            modulo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            aula = int(sys.argv[4]) if len(sys.argv) > 4 else 1
            
            if not os.path.exists(video_path):
                print(f"❌ Arquivo não encontrado: {video_path}")
                sys.exit(1)
                
            result = system.process_video_complete(video_path, modulo, aula)
            
            if result.get("status") == "success":
                sys.exit(0)
            else:
                print(f"❌ Erro no processamento: {result.get('message')}")
                sys.exit(1)
        else:
            print(f"❌ Comando não reconhecido: {command}")
            print("Use --help para ver os comandos disponíveis")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Processamento interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()