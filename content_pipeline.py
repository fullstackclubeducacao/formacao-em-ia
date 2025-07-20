#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Sistema Unificado de Produção de Conteúdo Educacional
=========================================================

Combina funcionalidades de:
- Transcrição avançada de vídeos (Groq Whisper)
- Análise inteligente de conteúdo (Google Gemini)
- Produção para YouTube (legendas, capítulos, shorts, metadados)
- Documentação automática (README, JSON, scripts)

Autor: Sistema Full Stack Club
Versão: 3.0.0 - Unificado
"""

import os
import sys
import json
import subprocess
import shutil
import datetime
import math
import time
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# --- IMPORTAÇÕES CONDICIONAIS ---
try:
    import google.generativeai as genai
    from google.generativeai import types
    from pydantic import BaseModel, Field
    from groq import Groq
    from PIL import Image
    from io import BytesIO
    import base64
    DEPENDENCIES_AVAILABLE = True
    GEMINI_AVAILABLE = True
    GROQ_AVAILABLE = True
    PIL_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    GEMINI_AVAILABLE = False
    GROQ_AVAILABLE = False
    PIL_AVAILABLE = False
    
    # Classes mock para evitar NameError
    class BaseModel:
        pass
    
    class Field:
        def __init__(self, **kwargs):
            pass
    
    print("❌ Dependências não encontradas:")
    print(f"   {e}")
    print("   Execute: ./instalar.sh para instalar todas as dependências")

# --- CONFIGURAÇÕES DINÂMICAS ---
# Todas as configurações podem ser alteradas via variáveis de ambiente

# Configurações de Transcrição
CHUNK_DURATION_SECONDS = int(os.environ.get("CHUNK_SIZE_SECONDS", "600"))  # 10 minutos
GROQ_MODEL = os.environ.get("GROQ_MODEL", "whisper-large-v3-turbo")
GROQ_LANGUAGE = os.environ.get("GROQ_LANGUAGE", "pt")

# Configurações de Sistema
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "300"))  # 5 minutos
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

# Caminhos de Sistema
FFMPEG_PATH = os.environ.get("FFMPEG_PATH", "./bin/ffmpeg")
FFPROBE_PATH = os.environ.get("FFPROBE_PATH", "./bin/ffprobe")
TEMP_DIR = os.environ.get("TEMP_DIR_NAME", "temp")
VIDEOS_DIR = os.environ.get("VIDEOS_DIR", "videos")

# Configurações de Áudio
AUDIO_SAMPLE_RATE = int(os.environ.get("AUDIO_SAMPLE_RATE", "16000"))
AUDIO_CHANNELS = int(os.environ.get("AUDIO_CHANNELS", "1"))
AUDIO_FORMAT = os.environ.get("AUDIO_FORMAT", "flac")

# Configurações YouTube
VIDEO_EXTENSIONS = ['.mp4', '.mkv', '.mov', '.avi', '.webm', '.m4v']
SUBTITLE_LANGUAGES = ['pt', 'en', 'es']

# Configurações de Geração de Imagens
IMAGE_GENERATION_MODELS = {
    "gemini": "gemini-2.0-flash-preview-image-generation",
    "imagen-3": "imagen-3.0-generate-002",
    "imagen-4": "imagen-4.0-generate-preview-06-06",
    "imagen-4-ultra": "imagen-4.0-ultra-generate-preview-06-06"
}

THUMBNAIL_ASPECT_RATIOS = {
    "youtube": "16:9",      # Padrão YouTube
    "shorts": "9:16",       # Padrão YouTube Shorts
    "square": "1:1",        # Quadrado
    "portrait": "3:4",      # Retrato
    "landscape": "4:3"      # Paisagem
}

# --- UTILITÁRIOS DE DEBUG ---
def debug_print(message: str):
    """Print debug se modo debug estiver ativo"""
    if DEBUG_MODE:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"🐛 [{timestamp}] {message}")

def format_duration(seconds: float) -> str:
    """Formata duração em formato legível"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}m {secs}s"

def print_header(title: str, char: str = "="):
    """Imprime cabeçalho formatado"""
    print(f"\n{char * 60}")
    print(f"🚀 {title}")
    print(f"{char * 60}")

def print_step(step: str, total: int, current: int):
    """Imprime etapa atual"""
    print(f"\n📍 Etapa {current}/{total}: {step}")
    print("-" * 40)

# --- MODELOS PYDANTIC UNIFICADOS ---
if DEPENDENCIES_AVAILABLE:
    # Modelos para Análise de Conteúdo
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

    # Modelos para YouTube
    class Chapter(BaseModel):
        timestamp: str = Field(description="Timestamp de início do capítulo no formato HH:MM:SS")
        title: str = Field(description="Título curto e descritivo para o capítulo")

    class ChaptersSchema(BaseModel):
        chapters: List[Chapter] = Field(description="Lista de capítulos do vídeo")

    class ShortIdea(BaseModel):
        titulo_sugestao: str = Field(description="Um título chamativo e curto para o Short")
        justificativa: str = Field(description="Breve explicação do porquê este clipe é uma boa escolha")
        timestamp_inicio: str = Field(description="Timestamp exato de início do clipe (HH:MM:SS)")
        timestamp_fim: str = Field(description="Timestamp exato de fim do clipe (HH:MM:SS)")

    class ShortsSchema(BaseModel):
        shorts_ideas: List[ShortIdea] = Field(description="Lista de 2 a 4 ideias para Shorts")

    class MetadataSchema(BaseModel):
        titles: List[str] = Field(description="Lista de 3 opções de títulos otimizados para SEO")
        description: str = Field(description="Descrição completa e otimizada para o vídeo, incluindo os capítulos e hashtags")
        tags: str = Field(description="String única contendo de 10 a 15 tags relevantes, separadas por vírgula")

    # Modelos para Geração de Thumbnails
    class ThumbnailIdea(BaseModel):
        titulo: str = Field(description="Título chamativo para o thumbnail")
        descricao_visual: str = Field(description="Descrição detalhada da imagem a ser gerada")
        estilo: str = Field(description="Estilo visual (ex: realista, cartoon, 3D, minimalista)")
        cores: str = Field(description="Paleta de cores sugerida")
        elementos_principais: List[str] = Field(description="Elementos visuais principais a incluir")

    class ThumbnailsSchema(BaseModel):
        thumbnails_video: List[ThumbnailIdea] = Field(description="3-5 ideias para thumbnails do vídeo principal")
        thumbnails_shorts: List[ThumbnailIdea] = Field(description="2-3 ideias para thumbnails dos shorts")

# --- DATACLASSES PARA RESULTADOS ---
@dataclass
class TranscriptionResult:
    """Resultado da transcrição"""
    text: str
    segments: List[Dict]
    words: List[Dict]
    duration: float
    metadata: Dict[str, Any]

@dataclass
class AnalysisResult:
    """Resultado da análise"""
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

# --- GERENCIADOR DE CONFIGURAÇÃO ---
class ConfigManager:
    """Gerencia configurações e validação de APIs"""
    
    def __init__(self):
        self.groq_client = None
        self.gemini_client = None
        self.gemini_model = None
        
        self.groq_available = False
        self.gemini_available = False
        self.ffmpeg_available = False
        
        self.setup_apis()
        self.check_dependencies()
    
    def setup_apis(self):
        """Configura e valida todas as APIs"""
        print("🔧 Configurando APIs...")
        
        # Configurar Groq
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and GROQ_AVAILABLE:
            try:
                self.groq_client = Groq(api_key=groq_key)
                self.groq_available = True
                print("✅ Groq configurado")
            except Exception as e:
                print(f"❌ Erro ao configurar Groq: {e}")
        else:
            print("❌ GROQ_API_KEY não encontrada ou biblioteca não instalada")
        
        # Configurar Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and GEMINI_AVAILABLE:
            try:
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
                self.gemini_available = True
                print(f"✅ Gemini configurado: gemini-2.5-flash")
                
                # Configurações opcionais
                thinking_enabled = os.getenv("GEMINI_THINKING", "true").lower() == "true"
                if thinking_enabled:
                    print("🧠 Thinking habilitado")
                
            except Exception as e:
                print(f"❌ Erro ao configurar Gemini: {e}")
        else:
            print("❌ GEMINI_API_KEY não encontrada ou biblioteca não instalada")
    
    def check_dependencies(self):
        """Verifica dependências do sistema"""
        # Verificar FFmpeg
        if shutil.which('ffmpeg') or os.path.exists(FFMPEG_PATH):
            self.ffmpeg_available = True
            print("✅ FFmpeg encontrado")
        else:
            print("❌ FFmpeg não encontrado - shorts desabilitados")
        
        # Verificar estrutura de diretórios
        os.makedirs(TEMP_DIR, exist_ok=True)
        os.makedirs(VIDEOS_DIR, exist_ok=True)
    
    def get_status(self) -> Dict[str, bool]:
        """Retorna status de todas as funcionalidades"""
        return {
            "transcrição": self.groq_available,
            "análise_ia": self.gemini_available,
            "shorts": self.ffmpeg_available and self.gemini_available,
            "legendas": self.gemini_available,
            "capítulos": self.gemini_available,
            "metadados": self.gemini_available,
            "thumbnails": self.gemini_available and PIL_AVAILABLE
        }
    
    def print_status(self):
        """Imprime status detalhado do sistema"""
        print("\n📊 Status do Sistema:")
        status = self.get_status()
        
        for funcionalidade, disponivel in status.items():
            icon = "✅" if disponivel else "❌"
            print(f"   {icon} {funcionalidade.title()}")
        
        if not any(status.values()):
            print("\n⚠️  Nenhuma funcionalidade disponível. Verifique configurações.")
        elif not status["transcrição"]:
            print("\n⚠️  Transcrição indisponível. Sistema não funcionará.")
        else:
            print(f"\n🎯 Sistema operacional - {sum(status.values())}/{len(status)} funcionalidades ativas")

# --- CLASSE PRINCIPAL UNIFICADA ---
class UnifiedContentPipeline:
    """Sistema unificado de produção de conteúdo educacional"""
    
    def __init__(self):
        self.config = ConfigManager()
    
    # --- MÓDULO 1: TRANSCRIÇÃO (TESTADO E FUNCIONAL) ---
    
    def get_audio_duration(self, file_path: str) -> Optional[float]:
        """Obtém a duração de um arquivo de mídia usando ffmpeg"""
        # Primeiro tenta usar ffprobe se existir
        if os.path.exists(FFPROBE_PATH):
            command = [
                FFPROBE_PATH,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ]
        else:
            # Fallback: usar ffmpeg para obter duração
            command = [
                FFMPEG_PATH,
                "-i", file_path,
                "-f", "null",
                "-"
            ]
        
        try:
            if os.path.exists(FFPROBE_PATH):
                # Usar ffprobe
                result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=REQUEST_TIMEOUT)
                duration = float(result.stdout)
            else:
                # Usar ffmpeg e extrair duração do stderr
                result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=REQUEST_TIMEOUT)
                
                # Extrair duração do stderr (ffmpeg mostra info no stderr)
                stderr_output = result.stderr
                
                # Procurar por padrão "Duration: HH:MM:SS.mm"
                import re
                duration_match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', stderr_output)
                
                if duration_match:
                    hours = int(duration_match.group(1))
                    minutes = int(duration_match.group(2))
                    seconds = int(duration_match.group(3))
                    centiseconds = int(duration_match.group(4))
                    
                    duration = hours * 3600 + minutes * 60 + seconds + centiseconds / 100.0
                else:
                    print(f"❌ Não foi possível extrair duração do vídeo")
                    return None
            
            debug_print(f"Audio duration: {duration:.2f}s for {file_path}")
            return duration
            
        except (subprocess.CalledProcessError, ValueError, subprocess.TimeoutExpired) as e:
            print(f"❌ Erro ao obter duração do áudio: {e}")
            return None
    
    def transcribe_video(self, video_path: str) -> Optional[TranscriptionResult]:
        """
        Transcreve vídeo usando a função original testada e funcional
        """
        print(f"📹 Iniciando transcrição: {os.path.basename(video_path)}")
        debug_print(f"Configurações: CHUNK_SIZE={CHUNK_DURATION_SECONDS}s, MODEL={GROQ_MODEL}")

        # Preparar caminhos
        base_name = os.path.basename(video_path)
        file_name, _ = os.path.splitext(base_name)
        temp_dir = TEMP_DIR
        final_transcription_path = os.path.join(temp_dir, f"{file_name}_transcription.json")

        # Obter duração e calcular chunks
        duration = self.get_audio_duration(video_path)
        if duration is None:
            return None
        
        num_chunks = math.ceil(duration / CHUNK_DURATION_SECONDS)
        print(f"⏱️  Duração: {format_duration(duration)}. Dividindo em {num_chunks} pedaço(s).")

        all_segments = []
        total_words = []
        transcribed_duration = 0.0

        for i in range(num_chunks):
            chunk_num = i + 1
            start_time = i * CHUNK_DURATION_SECONDS
            chunk_audio_path = os.path.join(temp_dir, f"{file_name}_chunk_{chunk_num}.{AUDIO_FORMAT}")
            
            print(f"\n--- Processando Pedaço {chunk_num}/{num_chunks} ---")
            print(f"🔄 Convertendo áudio (início: {start_time}s)...")

            # Converter um pedaço do vídeo para áudio
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
                subprocess.run(ffmpeg_command, check=True, capture_output=True, text=True, timeout=REQUEST_TIMEOUT)
                debug_print(f"FFmpeg success for chunk {chunk_num}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro no ffmpeg para o pedaço {chunk_num}: {e.stderr}")
                continue
            except subprocess.TimeoutExpired:
                print(f"⏰ Timeout no ffmpeg para o pedaço {chunk_num}")
                continue

            # Transcrever o pedaço com a API
            print(f"🎤 Enviando pedaço {chunk_num} para a API do Groq...")
            
            retry_count = 0
            transcription = None
            
            while retry_count < MAX_RETRIES and transcription is None:
                try:
                    with open(chunk_audio_path, "rb") as file:
                        transcription = self.config.groq_client.audio.transcriptions.create(
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
                    print(f"✅ Pedaço {chunk_num} transcrito com sucesso.")

                except Exception as e:
                    retry_count += 1
                    print(f"❌ Erro na transcrição do pedaço {chunk_num} (tentativa {retry_count}/{MAX_RETRIES}): {e}")
                    
                    if retry_count < MAX_RETRIES:
                        wait_time = 2 ** retry_count  # Backoff exponencial
                        print(f"⏳ Aguardando {wait_time}s antes da próxima tentativa...")
                        time.sleep(wait_time)
            
            # Limpar arquivo temporário
            if os.path.exists(chunk_audio_path):
                os.remove(chunk_audio_path)

        # Montar o JSON final
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

        print(f"\n✅ Transcrição concluída e salva em: {final_transcription_path}")
        debug_print(f"Final stats: {len(total_words)} words, {len(all_segments)} segments, {transcribed_duration:.2f}s")
        
        # Converter para TranscriptionResult
        return TranscriptionResult(
            text=final_result["text"],
            segments=final_result["segments"],
            words=final_result["words"],
            duration=final_result["duration"],
            metadata={
                "file_name": file_name,
                "original_path": video_path,
                "transcription_date": datetime.now().isoformat(),
                "chunks_processed": num_chunks
            }
        )
    
    # --- MÓDULO 2: ANÁLISE INTELIGENTE (TESTADO E FUNCIONAL) ---
    
    def analyze_content_with_gemini(self, transcription: TranscriptionResult) -> Optional[AnalysisResult]:
        """Analisa conteúdo transcrito usando Gemini com structured output"""
        if not self.config.gemini_available:
            print("⚠️  Gemini não disponível. Usando análise básica.")
            return self._basic_analysis(transcription)
            
        # Calcular tokens aproximados
        estimated_tokens = len(transcription.text) // 4
        max_context = int(os.getenv("GEMINI_MAX_CONTEXT", "1000000"))
        
        if estimated_tokens > max_context:
            # Truncar se necessário
            text_start = transcription.text[:max_context//3 * 4]
            text_end = transcription.text[-max_context//3 * 4:]
            text_sample = f"{text_start}\n\n[... CONTEÚDO INTERMEDIÁRIO OMITIDO ...]\n\n{text_end}"
            print(f"📊 Texto truncado: {estimated_tokens:,} → {max_context:,} tokens")
        else:
            text_sample = transcription.text
            print(f"📊 Processando {estimated_tokens:,} tokens de contexto")

        # System instruction otimizada
        system_instruction = """Você é um especialista em análise de conteúdo educacional técnico. 
        Sua função é extrair informações estruturadas de transcrições de aulas técnicas, 
        identificando conceitos, tecnologias, comandos e organizando o conhecimento de forma didática.
        
        Seja preciso, técnico e educativo. Extraia apenas informações que estão explicitamente 
        presentes na transcrição. Mantenha consistência terminológica."""

        # Prompt otimizado
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

Seja detalhado na análise e preciso nas informações extraídas."""

        try:
            print("🧠 Iniciando análise inteligente com Gemini...")
            
            # Configuração de geração com structured output
            response = self.config.gemini_model.generate_content(
                analysis_prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=AnalysisSchema,
                    temperature=0.1,
                    system_instruction=system_instruction,
                )
            )
            
            # Processar resposta structured output
            if hasattr(response, 'candidates') and response.candidates:
                response_text = response.candidates[0].content.parts[0].text
                analysis_data = json.loads(response_text)
            else:
                analysis_data = json.loads(response.text)
            
            # Converter conceitos para formato compatível
            conceitos_convertidos = []
            if 'conceitos_importantes' in analysis_data:
                for conceito in analysis_data['conceitos_importantes']:
                    if isinstance(conceito, dict):
                        conceitos_convertidos.append(conceito)
                    else:
                        conceitos_convertidos.append({
                            "conceito": conceito.conceito if hasattr(conceito, 'conceito') else str(conceito),
                            "definicao": conceito.definicao if hasattr(conceito, 'definicao') else ""
                        })
            
            # Converter para AnalysisResult
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
            
            # Mostrar estatísticas se disponível
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                print(f"📊 Tokens utilizados: {usage.total_token_count:,}")
            
            print("✅ Análise inteligente concluída com sucesso")
            return analysis
            
        except Exception as e:
            print(f"❌ Erro na análise Gemini: {e}")
            print("🔄 Tentando análise básica como fallback...")
            return self._basic_analysis(transcription)

    def _basic_analysis(self, transcription: TranscriptionResult) -> AnalysisResult:
        """Análise básica quando Gemini não está disponível"""
        file_name = transcription.metadata.get("file_name", "Aula")
        text = transcription.text.lower()
        
        # Detectar tecnologias comuns
        tech_keywords = {
            "docker": "Docker", "n8n": "N8N", "postgres": "PostgreSQL",
            "redis": "Redis", "traefik": "Traefik", "portainer": "Portainer",
            "javascript": "JavaScript", "python": "Python", "nodejs": "Node.js",
            "react": "React", "vue": "Vue.js", "api": "API", "webhook": "Webhook",
            "json": "JSON", "sql": "SQL", "html": "HTML", "css": "CSS"
        }
        
        detected_techs = [tech_name for keyword, tech_name in tech_keywords.items() if keyword in text]
        
        # Detectar comandos básicos
        command_patterns = [
            r'docker\s+\w+', r'npm\s+\w+', r'pip\s+\w+', r'git\s+\w+',
            r'sudo\s+\w+', r'chmod\s+\d+', r'mkdir\s+\w+', r'cd\s+\w+'
        ]
        
        detected_commands = []
        for pattern in command_patterns:
            matches = re.findall(pattern, text)
            detected_commands.extend(matches[:3])
        
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

    # --- MÓDULO 4: PRODUÇÃO PARA YOUTUBE ---
    
    @staticmethod
    def format_srt_timestamp(seconds: float) -> str:
        """Formata timestamp para formato SRT"""
        td = timedelta(seconds=seconds)
        total_seconds = int(td.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{int(seconds):02d},{milliseconds:03d}"
    
    def _translate_text_bulk(self, segments: List[Dict], target_language: str) -> List[str]:
        """Traduz segmentos em lote para o idioma especificado"""
        if not self.config.gemini_available:
            return [f"[{target_language.upper()}] {s['text']}" for s in segments]

        print(f"🌐 Traduzindo {len(segments)} segmentos para {target_language.upper()}...")
        
        # Traduzir em lotes menores para melhor controle
        batch_size = 10
        all_translated_texts = []
        
        for i in range(0, len(segments), batch_size):
            batch_segments = segments[i:i + batch_size]
            batch_texts = [seg['text'].strip() for seg in batch_segments]
            
            # Criar prompt mais específico para tradução
            if target_language == 'en':
                prompt = f"""Translate the following Portuguese text to English. Keep the educational context and mathematical terminology accurate.

Texts to translate:
{chr(10).join([f"{j+1}. {text}" for j, text in enumerate(batch_texts)])}

Return only the English translations, one per line, in the same order."""
            elif target_language == 'es':
                prompt = f"""Traduce el siguiente texto portugués al español. Mantén el contexto educativo y la terminología matemática precisa.

Textos a traducir:
{chr(10).join([f"{j+1}. {text}" for j, text in enumerate(batch_texts)])}

Devuelve solo las traducciones en español, una por línea, en el mismo orden."""
            else:
                # Para outros idiomas, usar abordagem genérica
                prompt = f"""Translate the following Portuguese text to {target_language}. Keep the educational context and mathematical terminology accurate.

Texts to translate:
{chr(10).join([f"{j+1}. {text}" for j, text in enumerate(batch_texts)])}

Return only the {target_language} translations, one per line, in the same order."""
            
            try:
                response = self.config.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.2,
                        max_output_tokens=4096
                    )
                )
                
                # Verificar se a resposta é válida
                if not response.text or response.text.strip() == "":
                    print(f"   ⚠️  Resposta vazia da API para lote {i//batch_size + 1}")
                    all_translated_texts.extend(batch_texts)  # Usar texto original
                    continue
                
                # Processar resposta linha por linha
                response_lines = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
                
                # Mapear traduções
                for j, original_text in enumerate(batch_texts):
                    if j < len(response_lines):
                        # Remover números e pontos do início da linha se existirem
                        translated_text = response_lines[j]
                        if translated_text and translated_text[0].isdigit():
                            # Remover "1. ", "2. ", etc.
                            translated_text = translated_text.split('. ', 1)[-1] if '. ' in translated_text else translated_text
                        all_translated_texts.append(translated_text)
                    else:
                        all_translated_texts.append(original_text)
                
                print(f"   ✅ Lote {i//batch_size + 1} traduzido ({len(batch_segments)} segmentos)")
                
            except Exception as e:
                print(f"   ❌ Erro na tradução do lote {i//batch_size + 1} para {target_language}: {e}")
                all_translated_texts.extend(batch_texts)  # Usar texto original em caso de erro
        
        # Garantir que temos o mesmo número de traduções que segmentos originais
        while len(all_translated_texts) < len(segments):
            all_translated_texts.append(segments[len(all_translated_texts)]['text'])
        
        return all_translated_texts[:len(segments)]
    
    def generate_subtitles(self, transcription: TranscriptionResult, output_path: Path, languages: List[str] = None) -> List[str]:
        """Gera legendas SRT em idiomas selecionados"""
        if not self.config.gemini_available:
            print("⚠️  Gemini não disponível. Legendas desabilitadas.")
            return []
        
        # Usar idiomas padrão se não especificados
        if languages is None:
            languages = SUBTITLE_LANGUAGES
        
        print(f"📝 Gerando legendas SRT em {len(languages)} idioma(s)...")
        
        generated_files = []
        original_segments = transcription.segments
        
        for lang in languages:
            srt_path = output_path / f'legenda_{lang}.srt'
            print(f"   🌐 Criando legenda em {lang.upper()}...")
            
            # Usar texto original para PT, traduzir para outros idiomas
            if lang == 'pt':
                translated_texts = [seg['text'].strip() for seg in original_segments]
            else:
                translated_texts = self._translate_text_bulk(original_segments, lang)
            
            # Escrever arquivo SRT
            with open(srt_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(original_segments):
                    f.write(f"{i + 1}\n")
                    f.write(f"{self.format_srt_timestamp(segment['start'])} --> {self.format_srt_timestamp(segment['end'])}\n")
                    f.write(f"{translated_texts[i]}\n\n")
            
            generated_files.append(str(srt_path))
            print(f"   ✅ Legenda '{srt_path.name}' criada")
        
        return generated_files
    
    def generate_chapters(self, transcription: TranscriptionResult) -> str:
        """Gera capítulos para YouTube"""
        if not self.config.gemini_available:
            print("⚠️  Gemini não disponível. Capítulos desabilitados.")
            return ""
        
        print("📖 Gerando capítulos para YouTube...")
        
        # Prompt para geração de capítulos
        prompt = f"""Analise esta transcrição de aula técnica e crie capítulos para YouTube.
        
        REGRAS:
        - O primeiro capítulo DEVE ser em 00:00:00
        - Criar 4-8 capítulos bem distribuídos
        - Títulos concisos e descritivos
        - Focar nos tópicos principais abordados
        
        CONTEXTO:
        - Duração total: {transcription.duration/60:.1f} minutos
        - Conteúdo: aula técnica educacional
        
        TRANSCRIÇÃO:
        {transcription.text[:8000]}"""  # Limitar para não exceder tokens
        
        try:
            response = self.config.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=ChaptersSchema,
                    temperature=0.2
                )
            )
            
            chapters_data = json.loads(response.text)['chapters']
            formatted_chapters = "\n".join([f"{c['timestamp']} - {c['title']}" for c in chapters_data])
            
            print("   ✅ Capítulos gerados com sucesso")
            return formatted_chapters
            
        except Exception as e:
            print(f"❌ Erro na geração de capítulos: {e}")
            return ""
    
    def generate_shorts(self, video_path: Path, transcription: TranscriptionResult, output_path: Path) -> List[str]:
        """Gera clipes para YouTube Shorts"""
        if not self.config.gemini_available or not self.config.ffmpeg_available:
            print("⚠️  Shorts requerem Gemini + FFmpeg. Funcionalidade desabilitada.")
            return []
        
        print("✂️  Gerando ideias para YouTube Shorts...")
        
        # Prompt para ideias de shorts
        prompt = f"""Analise esta transcrição e sugira 2-4 clipes de 30-60 segundos para YouTube Shorts.
        
        CRITÉRIOS:
        - Focar em dicas rápidas e práticas
        - Momentos de maior impacto educacional
        - Conceitos que podem ser entendidos isoladamente
        - Trechos com demonstrações visuais
        
        CONTEXTO:
        - Duração total: {transcription.duration/60:.1f} minutos
        - Tipo: aula técnica
        
        TRANSCRIÇÃO:
        {transcription.text[:10000]}"""  # Limitar texto
        
        try:
            response = self.config.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=ShortsSchema,
                    temperature=0.3
                )
            )
            
            shorts_ideas = json.loads(response.text)['shorts_ideas']
            shorts_output_path = output_path / "shorts"
            shorts_output_path.mkdir(exist_ok=True)
            
            generated_files = []
            
            for i, idea in enumerate(shorts_ideas):
                try:
                    files = self._process_single_short(i, idea, shorts_output_path, video_path, transcription)
                    generated_files.extend(files)
                except Exception as e:
                    print(f"❌ Erro no processamento do Short {i+1}: {e}")
                    continue
            
            return generated_files
            
        except Exception as e:
            print(f"❌ Erro na geração de Shorts: {e}")
            return []
    
    def _process_single_short(self, i: int, idea: Dict, shorts_output_path: Path, video_path: Path, transcription: TranscriptionResult) -> List[str]:
        """Processa um único short"""
        corte_dir = shorts_output_path / f"corte_{i+1}"
        corte_dir.mkdir(exist_ok=True)
        
        print(f"   ✂️  Processando Short {i+1}: '{idea['titulo_sugestao']}'")
        
        start_ts, end_ts = idea['timestamp_inicio'], idea['timestamp_fim']
        output_video_path = corte_dir / 'short_final.mp4'
        clip_srt_path = corte_dir / 'legenda_short.srt'
        info_file = corte_dir / 'info.txt'
        
        # Converter timestamps para segundos
        start_s = sum(x * int(t) for x, t in zip([3600, 60, 1], start_ts.split(':')))
        end_s = sum(x * int(t) for x, t in zip([3600, 60, 1], end_ts.split(':')))
        
        # Gerar legenda do clipe
        with open(clip_srt_path, 'w', encoding='utf-8') as f:
            count = 1
            for seg in transcription.segments:
                if start_s <= seg['start'] < end_s:
                    f.write(f"{count}\n")
                    f.write(f"{self.format_srt_timestamp(seg['start'] - start_s)} --> {self.format_srt_timestamp(seg['end'] - start_s)}\n")
                    f.write(f"{seg['text'].strip()}\n\n")
                    count += 1
        
        # Gerar informações do short
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write(f"TÍTULO SUGERIDO: {idea['titulo_sugestao']}\n\n")
            f.write(f"JUSTIFICATIVA: {idea['justificativa']}\n\n")
            f.write(f"TEMPO: {start_ts} - {end_ts}\n")
            f.write(f"DURAÇÃO: {end_s - start_s} segundos\n")
        
        # Comando FFmpeg para gerar vídeo com legendas
        ffmpeg_cmd = [
            FFMPEG_PATH, '-i', str(video_path),
            '-ss', start_ts, '-to', end_ts,
            '-vf', f"subtitles='{clip_srt_path}':force_style='FontName=Arial,FontSize=24,PrimaryColour=&Hffffff&,BackColour=&H80000000&,BorderStyle=4,Alignment=10'",
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-y', str(output_video_path)
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True, capture_output=True, text=True, timeout=300)
            print(f"      ✅ Vídeo '{output_video_path.name}' criado")
            return [str(output_video_path), str(clip_srt_path), str(info_file)]
        except subprocess.CalledProcessError as e:
            print(f"      ❌ Erro no FFmpeg: {e.stderr}")
            return []
    
    def generate_metadata(self, transcription: TranscriptionResult, chapters: str, output_path: Path) -> Optional[str]:
        """Gera metadados otimizados para YouTube"""
        if not self.config.gemini_available:
            print("⚠️  Gemini não disponível. Metadados desabilitados.")
            return None
        
        print("📋 Gerando metadados para YouTube...")
        
        # Prompt para metadados
        prompt = f"""Crie metadados otimizados para um vídeo educacional no YouTube.
        
        REQUISITOS:
        - 3 opções de títulos (máximo 60 caracteres cada)
        - 1 descrição completa e otimizada para SEO
        - Tags relevantes (10-15 tags)
        - Incluir os capítulos na descrição
        - Focar em educação técnica/programação
        
        CAPÍTULOS:
        {chapters}
        
        CONTEXTO:
        - Duração: {transcription.duration/60:.1f} minutos
        - Palavras: {len(transcription.words):,}
        - Tipo: aula técnica educacional
        
        TRANSCRIÇÃO (amostra):
        {transcription.text[:5000]}"""
        
        try:
            response = self.config.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=MetadataSchema,
                    temperature=0.4
                )
            )
            
            metadata = json.loads(response.text)
            output_file = output_path / 'metadata_youtube.txt'
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=== OPÇÕES DE TÍTULO ===\n")
                for i, title in enumerate(metadata.get('titles', []), 1):
                    f.write(f"{i}. {title}\n")
                
                f.write("\n=== DESCRIÇÃO SUGERIDA ===\n")
                f.write(metadata.get('description', '').strip())
                
                f.write("\n\n=== TAGS SUGERIDAS ===\n")
                f.write(metadata.get('tags', ''))
                
                if chapters:
                    f.write("\n\n=== CAPÍTULOS ===\n")
                    f.write(chapters)
            
            print(f"   ✅ Metadados salvos em '{output_file.name}'")
            return str(output_file)
            
        except Exception as e:
            print(f"❌ Erro na geração de metadados: {e}")
            return None

    def generate_thumbnail_ideas(self, transcription: TranscriptionResult, analysis: AnalysisResult) -> Optional[Dict]:
        """Gera ideias para thumbnails baseadas no conteúdo"""
        if not self.config.gemini_available:
            print("⚠️  Gemini não disponível. Thumbnails desabilitados.")
            return None
        
        print("🎨 Gerando ideias para thumbnails...")
        
        prompt = f"""Crie ideias criativas para thumbnails de um vídeo educacional no YouTube.
        
        CONTEXTO DO VÍDEO:
        - Título: {analysis.titulo_sugerido}
        - Resumo: {analysis.resumo_executivo}
        - Pontos-chave: {', '.join(analysis.pontos_chave)}
        - Tecnologias: {', '.join(analysis.tecnologias_mencionadas)}
        - Nível: {analysis.nivel_dificuldade}
        
        REQUISITOS:
        - 3-5 ideias para thumbnail do vídeo principal (16:9)
        - 2-3 ideias para thumbnails dos shorts (9:16)
        - Cada ideia deve incluir título, descrição visual, estilo, cores e elementos
        - Focar em elementos visuais chamativos e educacionais
        - Usar cores vibrantes e contrastantes
        - Incluir elementos que representem o conteúdo técnico
        
        TRANSCRIÇÃO (amostra):
        {transcription.text[:3000]}"""
        
        try:
            response = self.config.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=ThumbnailsSchema,
                    temperature=0.6
                )
            )
            
            thumbnails_data = json.loads(response.text)
            print("   ✅ Ideias para thumbnails geradas com sucesso")
            return thumbnails_data
            
        except Exception as e:
            print(f"❌ Erro na geração de ideias para thumbnails: {e}")
            return None

    def generate_thumbnail_image(self, prompt: str, model: str = "gemini", aspect_ratio: str = "16:9", 
                               output_path: Path = None, filename: str = "thumbnail") -> Optional[str]:
        """Gera uma imagem de thumbnail usando IA"""
        if not self.config.gemini_available or not PIL_AVAILABLE:
            print("⚠️  Geração de imagens requer Gemini + PIL. Funcionalidade desabilitada.")
            return None
        
        print(f"   🎨 Gerando thumbnail com {model}...")
        
        try:
            if model == "gemini":
                # Usar Gemini para geração de imagem
                response = self.config.gemini_model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        response_modalities=['TEXT', 'IMAGE'],
                        temperature=0.7
                    )
                )
                
                # Extrair imagem da resposta
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        image_data = part.inline_data.data
                        image = Image.open(BytesIO(image_data))
                        
                        # Salvar imagem
                        if output_path:
                            output_path.mkdir(parents=True, exist_ok=True)
                            image_path = output_path / f"{filename}.png"
                            image.save(image_path)
                            print(f"      ✅ Thumbnail salvo: {image_path}")
                            return str(image_path)
                        break
                        
            else:
                # Usar Imagen para geração de imagem
                client = genai.Client()
                
                # Configurar parâmetros do Imagen
                config_params = {
                    "number_of_images": 1,
                    "aspect_ratio": aspect_ratio
                }
                
                response = client.models.generate_images(
                    model=IMAGE_GENERATION_MODELS.get(model, model),
                    prompt=prompt,
                    config=types.GenerateImagesConfig(**config_params)
                )
                
                # Salvar primeira imagem gerada
                if response.generated_images:
                    image = response.generated_images[0].image
                    
                    if output_path:
                        output_path.mkdir(parents=True, exist_ok=True)
                        image_path = output_path / f"{filename}.png"
                        image.save(image_path)
                        print(f"      ✅ Thumbnail salvo: {image_path}")
                        return str(image_path)
            
            return None
            
        except Exception as e:
            print(f"      ❌ Erro na geração de thumbnail: {e}")
            return None

    def generate_all_thumbnails(self, transcription: TranscriptionResult, analysis: AnalysisResult, 
                               output_path: Path, model: str = "gemini", num_video_thumbnails: int = 3,
                               num_shorts_thumbnails: int = 2) -> List[str]:
        """Gera todas as thumbnails para vídeo e shorts"""
        if not self.config.gemini_available:
            print("⚠️  Gemini não disponível. Thumbnails desabilitados.")
            return []
        
        print("🎨 Gerando thumbnails para vídeo e shorts...")
        
        # Gerar ideias para thumbnails
        thumbnails_ideas = self.generate_thumbnail_ideas(transcription, analysis)
        if not thumbnails_ideas:
            return []
        
        generated_files = []
        thumbnails_dir = output_path / "thumbnails"
        thumbnails_dir.mkdir(exist_ok=True)
        
        # Gerar thumbnails para vídeo principal
        video_thumbnails_dir = thumbnails_dir / "video"
        video_thumbnails_dir.mkdir(exist_ok=True)
        
        print(f"   📹 Gerando {num_video_thumbnails} thumbnails para vídeo principal...")
        for i, idea in enumerate(thumbnails_ideas.get('thumbnails_video', [])[:num_video_thumbnails]):
            prompt = f"""Crie uma imagem de thumbnail para YouTube com as seguintes características:
            
            TÍTULO: {idea['titulo']}
            DESCRIÇÃO: {idea['descricao_visual']}
            ESTILO: {idea['estilo']}
            CORES: {idea['cores']}
            ELEMENTOS: {', '.join(idea['elementos_principais'])}
            
            REQUISITOS:
            - Formato 16:9 (YouTube)
            - Alta qualidade e resolução
            - Cores vibrantes e contrastantes
            - Texto legível e chamativo
            - Elementos educacionais visíveis
            - Estilo profissional e moderno"""
            
            image_path = self.generate_thumbnail_image(
                prompt=prompt,
                model=model,
                aspect_ratio="16:9",
                output_path=video_thumbnails_dir,
                filename=f"video_thumbnail_{i+1}"
            )
            
            if image_path:
                generated_files.append(image_path)
        
        # Gerar thumbnails para shorts
        shorts_thumbnails_dir = thumbnails_dir / "shorts"
        shorts_thumbnails_dir.mkdir(exist_ok=True)
        
        print(f"   📱 Gerando {num_shorts_thumbnails} thumbnails para shorts...")
        for i, idea in enumerate(thumbnails_ideas.get('thumbnails_shorts', [])[:num_shorts_thumbnails]):
            prompt = f"""Crie uma imagem de thumbnail para YouTube Shorts com as seguintes características:
            
            TÍTULO: {idea['titulo']}
            DESCRIÇÃO: {idea['descricao_visual']}
            ESTILO: {idea['estilo']}
            CORES: {idea['cores']}
            ELEMENTOS: {', '.join(idea['elementos_principais'])}
            
            REQUISITOS:
            - Formato 9:16 (YouTube Shorts)
            - Alta qualidade e resolução
            - Cores vibrantes e contrastantes
            - Texto legível e chamativo
            - Elementos educacionais visíveis
            - Estilo moderno e atrativo para mobile"""
            
            image_path = self.generate_thumbnail_image(
                prompt=prompt,
                model=model,
                aspect_ratio="9:16",
                output_path=shorts_thumbnails_dir,
                filename=f"shorts_thumbnail_{i+1}"
            )
            
            if image_path:
                generated_files.append(image_path)
        
        # Salvar ideias em arquivo de texto
        ideas_file = thumbnails_dir / "ideias_thumbnails.txt"
        with open(ideas_file, 'w', encoding='utf-8') as f:
            f.write("=== IDEIAS PARA THUMBNAILS ===\n\n")
            
            f.write("📹 THUMBNAILS PARA VÍDEO PRINCIPAL:\n")
            for i, idea in enumerate(thumbnails_ideas.get('thumbnails_video', []), 1):
                f.write(f"\n{i}. {idea['titulo']}\n")
                f.write(f"   Descrição: {idea['descricao_visual']}\n")
                f.write(f"   Estilo: {idea['estilo']}\n")
                f.write(f"   Cores: {idea['cores']}\n")
                f.write(f"   Elementos: {', '.join(idea['elementos_principais'])}\n")
            
            f.write("\n\n📱 THUMBNAILS PARA SHORTS:\n")
            for i, idea in enumerate(thumbnails_ideas.get('thumbnails_shorts', []), 1):
                f.write(f"\n{i}. {idea['titulo']}\n")
                f.write(f"   Descrição: {idea['descricao_visual']}\n")
                f.write(f"   Estilo: {idea['estilo']}\n")
                f.write(f"   Cores: {idea['cores']}\n")
                f.write(f"   Elementos: {', '.join(idea['elementos_principais'])}\n")
        
        generated_files.append(str(ideas_file))
        print(f"   ✅ {len(generated_files)} arquivos de thumbnail gerados")
        
        return generated_files

    # --- MÓDULO 3: DOCUMENTAÇÃO (TESTADO E FUNCIONAL) ---
    
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

    def generate_directory_structure(self, analysis: AnalysisResult, modulo: int, aula: int) -> Path:
        """Gera estrutura de diretórios para a aula"""
        slug = self.create_slug(analysis.titulo_sugerido)
        
        modulo_dir = f"modulo-{modulo:02d}"
        aula_dir = Path(modulo_dir) / f"aula-{aula:02d}-{slug}"
        
        # Criar diretórios
        aula_dir.mkdir(parents=True, exist_ok=True)
        (aula_dir / "assets").mkdir(exist_ok=True)
        (aula_dir / "scripts").mkdir(exist_ok=True)
        
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

    def save_analysis_files(self, transcription: TranscriptionResult, analysis: AnalysisResult, output_dir: Path) -> List[str]:
        """Salva todos os arquivos da análise"""
        files_created = []
        
        try:
            # 1. Salvar transcrição JSON
            transcription_path = output_dir / "transcricao.json"
            transcription_data = {
                "text": transcription.text,
                "segments": transcription.segments,
                "words": transcription.words,
                "duration": transcription.duration,
                "metadata": transcription.metadata
            }
            with open(transcription_path, "w", encoding="utf-8") as f:
                json.dump(transcription_data, f, ensure_ascii=False, indent=2)
            files_created.append(str(transcription_path))
            print(f"✅ Transcrição salva: {transcription_path}")
            
            # 2. Salvar análise JSON
            analysis_path = output_dir / "analise.json"
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
            files_created.append(str(analysis_path))
            print(f"✅ Análise salva: {analysis_path}")
            
            # 3. Gerar e salvar README
            readme_content = self.generate_readme_content(analysis, transcription)
            readme_path = output_dir / "README.md"
            with open(readme_path, "w", encoding="utf-8") as f:
                f.write(readme_content)
            files_created.append(str(readme_path))
            print(f"✅ README gerado: {readme_path}")
            
            # 4. Salvar comandos em arquivo separado se houver
            if analysis.comandos_codigo:
                scripts_dir = output_dir / "scripts"
                commands_file = scripts_dir / "comandos.md"
                with open(commands_file, "w", encoding="utf-8") as f:
                    f.write("# Comandos da Aula\n\n")
                    for i, cmd in enumerate(analysis.comandos_codigo, 1):
                        f.write(f"## Comando {i}\n```bash\n{cmd}\n```\n\n")
                files_created.append(str(commands_file))
                print(f"✅ Comandos salvos: {commands_file}")
                
        except Exception as e:
            print(f"❌ Erro ao salvar arquivos: {e}")
            
        return files_created
    
    # --- FUNÇÕES UTILITÁRIAS ---
    
    def find_videos(self, videos_dir: str = VIDEOS_DIR) -> List[Path]:
        """Encontra todos os vídeos no diretório especificado"""
        if not os.path.exists(videos_dir):
            return []
            
        video_files = []
        videos_path = Path(videos_dir)
        
        for ext in VIDEO_EXTENSIONS:
            video_files.extend(videos_path.glob(f"**/*{ext}"))
        
        return sorted(video_files)
    
    def extract_module_aula_from_filename(self, filename: str) -> Tuple[int, int]:
        """Extrai números de módulo e aula do nome do arquivo"""
        # Tentar extrair números do nome do arquivo
        modulo_match = re.search(r'modulo[-_]?(\d+)', filename, re.IGNORECASE)
        aula_match = re.search(r'aula[-_]?(\d+)', filename, re.IGNORECASE)
        
        modulo = int(modulo_match.group(1)) if modulo_match else 1
        aula = int(aula_match.group(1)) if aula_match else 1
        
        return modulo, aula 

    # --- MÓDULO 5: PIPELINE PRINCIPAL ---
    
    def process_video_complete(self, video_path: str, modulo: int = 1, aula: int = 1, 
                             include_subtitles: bool = False, include_chapters: bool = False,
                             include_shorts: bool = False, include_metadata: bool = False,
                             languages: List[str] = None) -> Dict[str, Any]:
        """Processa um vídeo completamente com todas as funcionalidades"""
        print_header(f"PROCESSAMENTO COMPLETO - {os.path.basename(video_path)}")
        
        try:
            # Etapa 1: Transcrição
            print_step("Transcrevendo vídeo", 7, 1)
            transcription = self.transcribe_video(video_path)
            if not transcription:
                return {"status": "error", "message": "Falha na transcrição"}
            
            # Etapa 2: Análise
            print_step("Analisando conteúdo", 7, 2)
            analysis = self.analyze_content_with_gemini(transcription)
            if not analysis:
                return {"status": "error", "message": "Falha na análise"}
            
            # Etapa 3: Estrutura de diretórios
            print_step("Criando estrutura", 7, 3)
            output_dir = self.generate_directory_structure(analysis, modulo, aula)
            
            # Etapa 4: Documentação básica
            print_step("Salvando documentação", 7, 4)
            files_created = self.save_analysis_files(transcription, analysis, output_dir)
            
            # Variáveis para funcionalidades YouTube
            chapters_content = ""
            subtitle_files = []
            shorts_files = []
            metadata_file = None
            
            # Etapa 5: Legendas (se solicitado)
            if include_subtitles:
                print_step("Gerando legendas SRT", 7, 5)
                subtitle_files = self.generate_subtitles(transcription, output_dir, languages)
                files_created.extend(subtitle_files)
            else:
                print("⏭️  Etapa 5/7: Legendas SRT - PULADA")
            
            # Etapa 6: Capítulos (se solicitado)
            if include_chapters:
                print_step("Gerando capítulos", 7, 6)
                chapters_content = self.generate_chapters(transcription)
                if chapters_content:
                    chapters_file = output_dir / "capitulos.txt"
                    with open(chapters_file, 'w', encoding='utf-8') as f:
                        f.write(chapters_content)
                    files_created.append(str(chapters_file))
                    print(f"✅ Capítulos salvos: {chapters_file}")
            else:
                print("⏭️  Etapa 6/7: Capítulos - PULADA")
                
            # Etapa 6.5: Shorts (se solicitado)
            if include_shorts:
                print_step("Gerando YouTube Shorts", 7, 6.5)
                shorts_files = self.generate_shorts(Path(video_path), transcription, output_dir)
                files_created.extend(shorts_files)
            else:
                print("⏭️  Shorts YouTube - PULADA")
            
            # Etapa 7: Metadados (se solicitado)
            if include_metadata:
                print_step("Gerando metadados YouTube", 7, 7)
                metadata_file = self.generate_metadata(transcription, chapters_content, output_dir)
                if metadata_file:
                    files_created.append(metadata_file)
            else:
                print("⏭️  Etapa 7/7: Metadados YouTube - PULADA")
            
            # Resultado final
            result = {
                "status": "success",
                "output_dir": str(output_dir),
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
                },
                "youtube_features": {
                    "subtitles": len(subtitle_files),
                    "chapters": bool(chapters_content),
                    "shorts": len([f for f in shorts_files if f.endswith('.mp4')]),
                    "metadata": bool(metadata_file)
                }
            }
            
            print_header("PROCESSAMENTO CONCLUÍDO COM SUCESSO!", "✅")
            print(f"📁 Aula criada em: {output_dir}")
            print(f"📊 Estatísticas:")
            print(f"   • Duração: {transcription.duration/60:.1f} minutos")
            print(f"   • Palavras: {len(transcription.words):,}")
            print(f"   • Tecnologias: {len(analysis.tecnologias_mencionadas)}")
            print(f"   • Conceitos: {len(analysis.conceitos_importantes)}")
            
            if any([include_subtitles, include_chapters, include_shorts, include_metadata]):
                print(f"🎬 Funcionalidades YouTube:")
                if include_subtitles:
                    print(f"   • Legendas: {len(subtitle_files)} idiomas")
                if include_chapters:
                    print(f"   • Capítulos: {'✅' if chapters_content else '❌'}")
                if include_shorts:
                    print(f"   • Shorts: {len([f for f in shorts_files if f.endswith('.mp4')])} vídeos")
                if include_metadata:
                    print(f"   • Metadados: {'✅' if metadata_file else '❌'}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERRO NO PROCESSAMENTO: {e}")
            return {"status": "error", "message": str(e)}

    def batch_process_videos(self, videos_dir: str = VIDEOS_DIR, start_modulo: int = 1,
                           include_youtube_features: bool = False) -> List[Dict[str, Any]]:
        """Processa todos os vídeos em lote"""
        print_header(f"PROCESSAMENTO EM LOTE - {videos_dir}")
        
        video_files = self.find_videos(videos_dir)
        
        if not video_files:
            print(f"❌ Nenhum vídeo encontrado em {videos_dir}")
            return []
            
        print(f"📹 Encontrados {len(video_files)} vídeos para processar")
        print("📁 Vídeos encontrados:")
        for i, video in enumerate(video_files, 1):
            print(f"   {i:2d}. {video.name}")
        
        results = []
        
        # Processar cada vídeo
        for i, video_path in enumerate(video_files, 1):
            print_header(f"VÍDEO {i}/{len(video_files)}: {video_path.name}")
            
            # Determinar módulo e aula
            modulo, aula = self.extract_module_aula_from_filename(video_path.stem)
            if modulo == 1:  # Se não detectou módulo no nome, usar sequencial
                modulo = start_modulo
                aula = i
            
            print(f"📊 Processando como: Módulo {modulo}, Aula {aula}")
            
            result = self.process_video_complete(
                str(video_path), modulo, aula,
                include_subtitles=include_youtube_features,
                include_chapters=include_youtube_features,
                include_shorts=include_youtube_features,
                include_metadata=include_youtube_features,
                languages=["pt", "en", "es"] if include_youtube_features else None
            )
            
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
        print_header("RELATÓRIO FINAL - PROCESSAMENTO EM LOTE", "📊")
        
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

    def process_existing_aula_for_youtube(self, aula_path: str, features: Dict[str, Any] = None) -> Dict[str, Any]:
        """Processa uma aula existente apenas para funcionalidades YouTube"""
        aula_dir = Path(aula_path)
        
        if not aula_dir.exists():
            return {"status": "error", "message": "Diretório da aula não encontrado"}
        
        # Procurar arquivos necessários
        transcricao_file = aula_dir / "transcricao.json"
        video_file = None
        
        # 1. Primeiro procura o vídeo na pasta da aula
        for ext in VIDEO_EXTENSIONS:
            video_candidates = list(aula_dir.glob(f"*{ext}"))
            if video_candidates:
                video_file = video_candidates[0]
                print(f"   ✅ Vídeo encontrado na pasta da aula: {video_file.name}")
                break
        
        # 2. Se não encontrou na aula, procura na pasta videos/
        if not video_file:
            videos_dir = Path(VIDEOS_DIR)
            if videos_dir.exists():
                # Tenta encontrar vídeo com nome similar à aula
                aula_name = aula_dir.name
                print(f"   🔍 Procurando vídeo na pasta '{VIDEOS_DIR}' para aula: {aula_name}")
                
                for ext in VIDEO_EXTENSIONS:
                    video_candidates = list(videos_dir.glob(f"*{ext}"))
                    if video_candidates:
                        # Se há apenas um vídeo, usa ele
                        if len(video_candidates) == 1:
                            video_file = video_candidates[0]
                            print(f"   ✅ Vídeo único encontrado: {video_file.name}")
                            break
                        else:
                            # Se há múltiplos vídeos, tenta fazer correspondência
                            for candidate in video_candidates:
                                candidate_name = candidate.stem.lower()
                                aula_name_lower = aula_name.lower()
                                
                                # Verifica se há palavras em comum
                                if any(word in candidate_name for word in aula_name_lower.split('-')) or \
                                   any(word in aula_name_lower for word in candidate_name.split('-') if len(word) > 2):
                                    video_file = candidate
                                    print(f"   ✅ Vídeo correspondente encontrado: {video_file.name}")
                                    break
                            
                            if video_file:
                                break
                
                if not video_file and video_candidates:
                    # Se não conseguiu fazer correspondência mas há vídeos, usa o primeiro
                    video_file = video_candidates[0]
                    print(f"   ⚠️  Usando primeiro vídeo disponível: {video_file.name}")
        
        if not transcricao_file.exists():
            return {"status": "error", "message": "Arquivo de transcrição não encontrado"}
        
        if not video_file:
            return {"status": "error", "message": "Arquivo de vídeo não encontrado"}
        
        print_header(f"PRODUÇÃO YOUTUBE - {aula_dir.name}")
        
        try:
            # Carregar transcrição existente
            with open(transcricao_file, 'r', encoding='utf-8') as f:
                transcription_data = json.load(f)
            
            # Converter para TranscriptionResult
            transcription = TranscriptionResult(
                text=transcription_data["text"],
                segments=transcription_data["segments"],
                words=transcription_data["words"],
                duration=transcription_data["duration"],
                metadata=transcription_data.get("metadata", {})
            )
            
            files_created = []
            
            # Usar configurações padrão se não fornecidas
            if features is None:
                features = {
                    "subtitles": True,
                    "languages": ["pt", "en", "es"],
                    "chapters": True,
                    "shorts": True,
                    "metadata": True,
                    "thumbnails": True
                }
            
            # Contar etapas ativas
            active_steps = sum([
                features.get("subtitles", False),
                features.get("chapters", False),
                features.get("shorts", False),
                features.get("metadata", False),
                features.get("thumbnails", False)
            ])
            
            step_counter = 1
            
            # Etapa 1: Gerar legendas SRT (opcional)
            if features.get("subtitles", False):
                print_step("Gerando legendas SRT", active_steps, step_counter)
                languages = features.get("languages", ["pt", "en", "es"])
                subtitle_files = self.generate_subtitles(transcription, aula_dir, languages)
                files_created.extend(subtitle_files)
                step_counter += 1
            else:
                print("   ⏭️  Legendas desabilitadas pelo usuário")
                subtitle_files = []
            
            # Etapa 2: Gerar capítulos (opcional)
            if features.get("chapters", False):
                print_step("Gerando capítulos", active_steps, step_counter)
                chapters_content = self.generate_chapters(transcription)
                if chapters_content:
                    chapters_file = aula_dir / "capitulos.txt"
                    with open(chapters_file, 'w', encoding='utf-8') as f:
                        f.write(chapters_content)
                    files_created.append(str(chapters_file))
                    print(f"✅ Capítulos salvos: {chapters_file}")
                step_counter += 1
            else:
                print("   ⏭️  Capítulos desabilitados pelo usuário")
                chapters_content = ""
            
            # Etapa 3: Gerar YouTube Shorts (opcional)
            if features.get("shorts", False):
                print_step("Gerando YouTube Shorts", active_steps, step_counter)
                shorts_files = self.generate_shorts(video_file, transcription, aula_dir)
                files_created.extend(shorts_files)
                step_counter += 1
            else:
                print("   ⏭️  Shorts desabilitados pelo usuário")
                shorts_files = []
            
            # Etapa 4: Gerar metadados (opcional)
            if features.get("metadata", False):
                print_step("Gerando metadados YouTube", active_steps, step_counter)
                metadata_file = self.generate_metadata(transcription, chapters_content, aula_dir)
                if metadata_file:
                    files_created.append(metadata_file)
                step_counter += 1
            else:
                print("   ⏭️  Metadados desabilitados pelo usuário")
                metadata_file = None
            
            # Etapa 5: Gerar thumbnails (opcional)
            if features.get("thumbnails", False):
                print_step("Gerando thumbnails", active_steps, step_counter)
                model = features.get("model", "gemini")
                num_video = features.get("num_video_thumbnails", 3)
                num_shorts = features.get("num_shorts_thumbnails", 2)
                
                # Precisa de análise para thumbnails
                analysis = self.analyze_content_with_gemini(transcription)
                if analysis:
                    thumbnail_files = self.generate_all_thumbnails(
                        transcription=transcription,
                        analysis=analysis,
                        output_path=aula_dir,
                        model=model,
                        num_video_thumbnails=num_video,
                        num_shorts_thumbnails=num_shorts
                    )
                    files_created.extend(thumbnail_files)
                else:
                    print("   ❌ Análise não disponível para thumbnails")
                    thumbnail_files = []
            else:
                print("   ⏭️  Thumbnails desabilitados pelo usuário")
                thumbnail_files = []
            
            result = {
                "status": "success",
                "output_dir": str(aula_dir),
                "files_created": files_created,
                "youtube_features": {
                    "subtitles": len(subtitle_files),
                    "chapters": bool(chapters_content),
                    "shorts": len([f for f in shorts_files if f.endswith('.mp4')]),
                    "metadata": bool(metadata_file),
                    "thumbnails": len([f for f in thumbnail_files if f.endswith('.png')])
                }
            }
            
            print_header("PRODUÇÃO YOUTUBE CONCLUÍDA!", "✅")
            print(f"📁 Arquivos criados em: {aula_dir}")
            print(f"🎬 Funcionalidades adicionadas:")
            print(f"   • Legendas: {len(subtitle_files)} idiomas")
            print(f"   • Capítulos: {'✅' if chapters_content else '❌'}")
            print(f"   • Shorts: {len([f for f in shorts_files if f.endswith('.mp4')])} vídeos")
            print(f"   • Metadados: {'✅' if metadata_file else '❌'}")
            print(f"   • Thumbnails: {len([f for f in thumbnail_files if f.endswith('.png')])} imagens")
            
            return result
            
        except Exception as e:
            print(f"❌ ERRO NO PROCESSAMENTO YOUTUBE: {e}")
            return {"status": "error", "message": str(e)} 

# --- INTERFACE INTERATIVA ---

class InteractiveMenu:
    """Menu interativo para o sistema unificado"""
    
    def __init__(self, pipeline: UnifiedContentPipeline):
        self.pipeline = pipeline
    
    def show_header(self):
        """Mostra cabeçalho do sistema"""
        print(f"\n{'='*80}")
        print("🤖 SISTEMA UNIFICADO DE PRODUÇÃO DE CONTEÚDO EDUCACIONAL")
        print("   Transcrição • Análise IA • Documentação • YouTube")
        print(f"{'='*80}")
        
        # Mostrar status do sistema
        self.pipeline.config.print_status()
    
    def get_video_choice(self) -> Optional[Path]:
        """Permite ao usuário escolher um vídeo"""
        videos = self.pipeline.find_videos()
        
        if not videos:
            print(f"\n❌ Nenhum vídeo encontrado no diretório '{VIDEOS_DIR}'")
            print(f"   Coloque seus vídeos na pasta '{VIDEOS_DIR}' e tente novamente.")
            return None
        
        print(f"\n📹 Vídeos disponíveis:")
        for i, video in enumerate(videos, 1):
            size_mb = video.stat().st_size / (1024 * 1024)
            print(f"   {i}. {video.name} ({size_mb:.1f}MB)")
        
        while True:
            try:
                choice = input(f"\n❓ Escolha um vídeo (1-{len(videos)}) ou 'q' para voltar: ").strip()
                if choice.lower() == 'q':
                    return None
                
                idx = int(choice) - 1
                if 0 <= idx < len(videos):
                    return videos[idx]
                else:
                    print(f"❌ Escolha inválida. Digite um número entre 1 e {len(videos)}.")
            except ValueError:
                print("❌ Digite um número válido.")
    
    def get_module_aula(self, video_path: Path) -> Tuple[int, int]:
        """Obtém números de módulo e aula"""
        # Tentar detectar automaticamente
        auto_modulo, auto_aula = self.pipeline.extract_module_aula_from_filename(video_path.stem)
        
        print(f"\n📊 Configuração da aula:")
        print(f"   Vídeo: {video_path.name}")
        
        if auto_modulo != 1 or auto_aula != 1:
            print(f"   📤 Detectado automaticamente: Módulo {auto_modulo}, Aula {auto_aula}")
            use_auto = input("   ❓ Usar detecção automática? (s/N): ").strip().lower()
            if use_auto == 's':
                return auto_modulo, auto_aula
        
        # Entrada manual
        while True:
            try:
                modulo = int(input("   ❓ Número do módulo (ex: 3): ").strip())
                if modulo > 0:
                    break
                print("   ❌ Módulo deve ser maior que 0.")
            except ValueError:
                print("   ❌ Digite um número válido.")
        
        while True:
            try:
                aula = int(input("   ❓ Número da aula (ex: 1): ").strip())
                if aula > 0:
                    break
                print("   ❌ Aula deve ser maior que 0.")
            except ValueError:
                print("   ❌ Digite um número válido.")
        
        return modulo, aula
    
    def get_youtube_features(self) -> Dict[str, Any]:
        """Permite escolher funcionalidades YouTube"""
        if not self.pipeline.config.gemini_available:
            print("\n⚠️  Funcionalidades YouTube requerem Gemini API. Desabilitadas.")
            return {"subtitles": False, "chapters": False, "shorts": False, "metadata": False, "thumbnails": False}
        
        print(f"\n🎬 Funcionalidades YouTube (opcional):")
        print("   Marque as funcionalidades desejadas:")
        
        features = {}
        
        # Legendas
        choice = input("   📝 Gerar legendas SRT? (s/N): ").strip().lower()
        features["subtitles"] = choice == 's'
        
        if features["subtitles"]:
            features["languages"] = self.get_subtitle_languages()
        
        # Capítulos
        choice = input("   📖 Gerar capítulos para YouTube? (s/N): ").strip().lower()
        features["chapters"] = choice == 's'
        
        # Shorts (só se FFmpeg disponível)
        if self.pipeline.config.ffmpeg_available:
            choice = input("   ✂️  Gerar YouTube Shorts automáticos? (s/N): ").strip().lower()
            features["shorts"] = choice == 's'
        else:
            print("   ✂️  Shorts desabilitados (FFmpeg não encontrado)")
            features["shorts"] = False
        
        # Metadados
        choice = input("   📋 Gerar metadados (títulos/descrição/tags)? (s/N): ").strip().lower()
        features["metadata"] = choice == 's'
        
        # Thumbnails
        if self.pipeline.config.gemini_available and PIL_AVAILABLE:
            choice = input("   🎨 Gerar thumbnails com IA? (s/N): ").strip().lower()
            features["thumbnails"] = choice == 's'
            
            if features["thumbnails"]:
                features.update(self.get_thumbnail_config())
        else:
            print("   🎨 Thumbnails desabilitados (Gemini + PIL não encontrados)")
            features["thumbnails"] = False
        
        return features

    def get_subtitle_languages(self) -> List[str]:
        """Permite escolher idiomas para legendas"""
        print(f"\n🌐 Idiomas disponíveis para legendas:")
        print("   1. Português (PT) - Original")
        print("   2. Inglês (EN) - Traduzido")
        print("   3. Espanhol (ES) - Traduzido")
        print("   4. Todos os idiomas")
        
        while True:
            choice = input("   ❓ Escolha a opção (1-4): ").strip()
            
            if choice == "1":
                return ["pt"]
            elif choice == "2":
                return ["pt", "en"]
            elif choice == "3":
                return ["pt", "es"]
            elif choice == "4":
                return ["pt", "en", "es"]
            else:
                print("   ❌ Escolha inválida. Digite um número entre 1 e 4.")

    def get_thumbnail_config(self) -> Dict[str, Any]:
        """Obtém configurações específicas para thumbnails"""
        config = {}
        
        print(f"\n🎨 Configurações de Thumbnails:")
        
        # Modelo de IA
        print("   Modelos disponíveis:")
        for i, (key, model) in enumerate(IMAGE_GENERATION_MODELS.items(), 1):
            print(f"   {i}. {key} ({model})")
        
        while True:
            try:
                choice = input("   ❓ Escolha o modelo (1-4): ").strip()
                model_keys = list(IMAGE_GENERATION_MODELS.keys())
                idx = int(choice) - 1
                if 0 <= idx < len(model_keys):
                    config["model"] = model_keys[idx]
                    break
                print("   ❌ Escolha inválida. Digite um número entre 1 e 4.")
            except ValueError:
                print("   ❌ Digite um número válido.")
        
        # Quantidade de thumbnails para vídeo
        while True:
            try:
                num_video = int(input("   ❓ Quantas thumbnails para vídeo principal? (1-5): ").strip())
                if 1 <= num_video <= 5:
                    config["num_video_thumbnails"] = num_video
                    break
                print("   ❌ Quantidade deve ser entre 1 e 5.")
            except ValueError:
                print("   ❌ Digite um número válido.")
        
        # Quantidade de thumbnails para shorts
        while True:
            try:
                num_shorts = int(input("   ❓ Quantas thumbnails para shorts? (1-3): ").strip())
                if 1 <= num_shorts <= 3:
                    config["num_shorts_thumbnails"] = num_shorts
                    break
                print("   ❌ Quantidade deve ser entre 1 e 3.")
            except ValueError:
                print("   ❌ Digite um número válido.")
        
        return config

    def show_confirmation_youtube(self, aula_path: Path, features: Dict[str, Any]) -> bool:
        """Mostra confirmação para processamento YouTube"""
        print(f"\n📋 RESUMO DO PROCESSAMENTO:")
        print(f"   📁 Aula: {aula_path.name}")
        print(f"   🎬 Funcionalidades selecionadas:")
        
        if features.get("subtitles", False):
            languages = features.get("languages", [])
            print(f"      📝 Legendas: {', '.join(languages)}")
        else:
            print(f"      📝 Legendas: ❌")
        
        print(f"      📖 Capítulos: {'✅' if features.get('chapters', False) else '❌'}")
        print(f"      ✂️  Shorts: {'✅' if features.get('shorts', False) else '❌'}")
        print(f"      📋 Metadados: {'✅' if features.get('metadata', False) else '❌'}")
        
        if features.get("thumbnails", False):
            model = features.get("model", "gemini")
            num_video = features.get("num_video_thumbnails", 3)
            num_shorts = features.get("num_shorts_thumbnails", 2)
            print(f"      🎨 Thumbnails: ✅ ({model}, {num_video} vídeo + {num_shorts} shorts)")
        else:
            print(f"      🎨 Thumbnails: ❌")
        
        choice = input(f"\n❓ Confirmar processamento? (s/N): ").strip().lower()
        return choice == 's'
    
    def show_confirmation(self, video_path: Path, modulo: int, aula: int, features: Dict[str, Any]) -> bool:
        """Mostra confirmação final"""
        print(f"\n{'='*60}")
        print("📋 CONFIRMAÇÃO DO PROCESSAMENTO")
        print(f"{'='*60}")
        print(f"📹 Vídeo: {video_path.name}")
        print(f"📊 Módulo: {modulo} | Aula: {aula}")
        print(f"🎬 Funcionalidades YouTube:")
        
        # Mostrar apenas as funcionalidades booleanas
        boolean_features = {
            "subtitles": "Legendas SRT",
            "chapters": "Capítulos",
            "shorts": "YouTube Shorts", 
            "metadata": "Metadados"
        }
        
        for feature, name in boolean_features.items():
            enabled = features.get(feature, False)
            icon = "✅" if enabled else "❌"
            print(f"   {icon} {name}")
            
            # Mostrar idiomas se legendas estiverem habilitadas
            if feature == "subtitles" and enabled:
                languages = features.get("languages", ["pt"])
                print(f"      🌐 Idiomas: {', '.join(languages)}")
        
        # Estimativa de tempo
        base_time = 3  # minutos base
        if features.get("subtitles", False): base_time += 2
        if features.get("chapters", False): base_time += 1
        if features.get("shorts", False): base_time += 5
        if features.get("metadata", False): base_time += 1
        
        print(f"\n⏱️  Tempo estimado: ~{base_time} minutos")
        
        confirm = input(f"\n❓ Confirma o processamento? (s/N): ").strip().lower()
        return confirm == 's'
    
    def find_existing_aulas(self) -> List[Path]:
        """Encontra aulas já processadas"""
        aulas = []
        
        # Procurar por diretórios com transcricao.json
        for modulo_dir in Path('.').glob('modulo-*'):
            if modulo_dir.is_dir():
                for aula_dir in modulo_dir.glob('aula-*'):
                    if aula_dir.is_dir() and (aula_dir / 'transcricao.json').exists():
                        aulas.append(aula_dir)
        
        return sorted(aulas)
    
    def menu_individual(self):
        """Menu para processamento individual"""
        print_header("MODO INDIVIDUAL")
        
        # Escolher vídeo
        video_path = self.get_video_choice()
        if not video_path:
            return
        
        # Configurar módulo e aula
        modulo, aula = self.get_module_aula(video_path)
        
        # Escolher funcionalidades YouTube
        features = self.get_youtube_features()
        
        # Confirmação
        if not self.show_confirmation(video_path, modulo, aula, features):
            print("❌ Processamento cancelado.")
            return
        
        # Executar processamento
        try:
            result = self.pipeline.process_video_complete(
                str(video_path), modulo, aula,
                include_subtitles=features["subtitles"],
                include_chapters=features["chapters"],
                include_shorts=features["shorts"],
                include_metadata=features["metadata"],
                languages=features.get("languages", ["pt"])
            )
            
            if result["status"] == "success":
                print(f"\n🎉 Processamento concluído com sucesso!")
                print(f"📁 Verifique os arquivos em: {result['output_dir']}")
            else:
                print(f"\n❌ Erro no processamento: {result['message']}")
                
        except KeyError as e:
            print(f"\n❌ Erro de configuração: {e}")
            print("   Verifique se todas as funcionalidades foram configuradas corretamente.")
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("   Tente novamente ou use o modo simples (opção 4).")
    
    def menu_batch(self):
        """Menu para processamento em lote"""
        print_header("MODO LOTE")
        
        videos = self.pipeline.find_videos()
        if not videos:
            print(f"❌ Nenhum vídeo encontrado em '{VIDEOS_DIR}'")
            return
        
        print(f"📹 {len(videos)} vídeos encontrados para processamento em lote:")
        for i, video in enumerate(videos, 1):
            print(f"   {i}. {video.name}")
        
        # Configurações do lote
        while True:
            try:
                start_modulo = int(input(f"\n❓ Módulo inicial (padrão: 1): ").strip() or "1")
                break
            except ValueError:
                print("❌ Digite um número válido.")
        
        # Funcionalidades YouTube para todo o lote
        print(f"\n🎬 Aplicar funcionalidades YouTube a todos os vídeos?")
        include_youtube = input("   (Legendas, capítulos, shorts, metadados) (s/N): ").strip().lower() == 's'
        
        # Confirmação
        print(f"\n📋 Processamento em lote:")
        print(f"   • {len(videos)} vídeos")
        print(f"   • Módulo inicial: {start_modulo}")
        print(f"   • YouTube: {'✅' if include_youtube else '❌'}")
        
        confirm = input(f"\n❓ Confirma? (s/N): ").strip().lower()
        if confirm != 's':
            print("❌ Processamento cancelado.")
            return
        
        # Executar lote
        results = self.pipeline.batch_process_videos(VIDEOS_DIR, start_modulo, include_youtube)
        
        successful = len([r for r in results if r.get("status") == "success"])
        print(f"\n🎉 Lote concluído: {successful}/{len(results)} vídeos processados com sucesso!")
    
    def menu_youtube_only(self):
        """Menu para produção YouTube de aulas existentes"""
        print_header("MODO YOUTUBE")
        
        aulas = self.find_existing_aulas()
        if not aulas:
            print("❌ Nenhuma aula processada encontrada.")
            print("   Execute primeiro o modo Individual ou Lote para criar aulas.")
            return
        
        print(f"📁 Aulas disponíveis para produção YouTube:")
        for i, aula in enumerate(aulas, 1):
            print(f"   {i}. {aula.name}")
        
        while True:
            try:
                choice = input(f"\n❓ Escolha uma aula (1-{len(aulas)}) ou 'q' para voltar: ").strip()
                if choice.lower() == 'q':
                    return
                
                idx = int(choice) - 1
                if 0 <= idx < len(aulas):
                    selected_aula = aulas[idx]
                    break
                else:
                    print(f"❌ Escolha inválida. Digite um número entre 1 e {len(aulas)}.")
            except ValueError:
                print("❌ Digite um número válido.")
        
        # Obter configurações do usuário
        features = self.get_youtube_features()
        
        # Mostrar confirmação
        if self.show_confirmation_youtube(selected_aula, features):
            # Executar produção YouTube
            result = self.pipeline.process_existing_aula_for_youtube(str(selected_aula), features)
        else:
            print("❌ Operação cancelada pelo usuário.")
            return
        
        if result["status"] == "success":
            print(f"\n🎉 Produção YouTube concluída!")
            print(f"📁 Verifique os arquivos em: {result['output_dir']}")
        else:
            print(f"\n❌ Erro: {result['message']}")
    
    def menu_simple(self):
        """Menu para transcrição simples (compatibilidade)"""
        print_header("MODO SIMPLES (TRANSCRIÇÃO)")
        print("⚠️  Modo de compatibilidade - apenas transcrição")
        
        video_path = self.get_video_choice()
        if not video_path:
            return
        
        print(f"\n📹 Transcrevendo: {video_path.name}")
        transcription = self.pipeline.transcribe_video(str(video_path))
        
        if transcription:
            print("✅ Transcrição concluída!")
            temp_file = Path(TEMP_DIR) / f"{video_path.stem}_transcription.json"
            print(f"📁 Arquivo salvo em: {temp_file}")
        else:
            print("❌ Falha na transcrição.")
    
    def run(self):
        """Executa o menu principal"""
        while True:
            self.show_header()
            
            print(f"\n🎯 MODOS DISPONÍVEIS:")
            print("   1. 📹 INDIVIDUAL - Processar um vídeo específico")
            print("   2. 📦 LOTE - Processar todos os vídeos")
            print("   3. 🎬 YOUTUBE - Produzir conteúdo YouTube de aula existente")
            print("   4. ⚡ SIMPLES - Apenas transcrição (modo compatibilidade)")
            print("   5. ⚙️  STATUS - Ver status do sistema")
            print("   6. ❌ SAIR")
            
            choice = input(f"\n❓ Escolha uma opção (1-6): ").strip()
            
            try:
                if choice == '1':
                    self.menu_individual()
                elif choice == '2':
                    self.menu_batch()
                elif choice == '3':
                    self.menu_youtube_only()
                elif choice == '4':
                    self.menu_simple()
                elif choice == '5':
                    self.pipeline.config.print_status()
                    input("\n⏎ Pressione Enter para continuar...")
                elif choice == '6':
                    print("\n👋 Obrigado por usar o Sistema Unificado!")
                    break
                else:
                    print("❌ Opção inválida. Tente novamente.")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Operação interrompida pelo usuário.")
            except Exception as e:
                print(f"\n❌ Erro inesperado: {e}")
                print("   Voltando ao menu principal...")
            
            if choice in ['1', '2', '3', '4']:
                input(f"\n⏎ Pressione Enter para voltar ao menu principal...")

# --- FUNÇÃO PRINCIPAL ---

def main():
    """Função principal com suporte a linha de comando e menu interativo"""
    
    # Verificar modo de compatibilidade (transcribe.py original)
    if len(sys.argv) == 2 and os.path.exists(sys.argv[1]) and not sys.argv[1].startswith('--'):
        print("🔄 Modo compatibilidade com transcribe.py")
        pipeline = UnifiedContentPipeline()
        result = pipeline.transcribe_video(sys.argv[1])
        sys.exit(0 if result else 1)
    
    # Modo linha de comando avançado
    if len(sys.argv) > 1:
        pipeline = UnifiedContentPipeline()
        
        command = sys.argv[1]
        
        if command == "--complete":
            if len(sys.argv) < 3:
                print("❌ Uso: python content_pipeline.py --complete video.mp4 [modulo] [aula]")
                sys.exit(1)
            
            video_path = sys.argv[2]
            modulo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            aula = int(sys.argv[4]) if len(sys.argv) > 4 else 1
            
            if not os.path.exists(video_path):
                print(f"❌ Vídeo não encontrado: {video_path}")
                sys.exit(1)
            
            result = pipeline.process_video_complete(video_path, modulo, aula, languages=["pt"])
            sys.exit(0 if result["status"] == "success" else 1)
            
        elif command == "--batch":
            videos_dir = sys.argv[2] if len(sys.argv) > 2 else VIDEOS_DIR
            start_modulo = int(sys.argv[3]) if len(sys.argv) > 3 else 1
            
            results = pipeline.batch_process_videos(videos_dir, start_modulo)
            successful = len([r for r in results if r.get("status") == "success"])
            sys.exit(0 if successful > 0 else 1)
            
        elif command == "--youtube":
            if len(sys.argv) < 3:
                print("❌ Uso: python content_pipeline.py --youtube aula_diretorio")
                sys.exit(1)
            
            aula_path = sys.argv[2]
            
            # Configurações padrão para linha de comando
            features = {
                "subtitles": True,
                "languages": ["pt", "en", "es"],
                "chapters": True,
                "shorts": True,
                "metadata": True,
                "thumbnails": True,
                "model": "gemini",
                "num_video_thumbnails": 3,
                "num_shorts_thumbnails": 2
            }
            
            result = pipeline.process_existing_aula_for_youtube(aula_path, features)
            sys.exit(0 if result["status"] == "success" else 1)
            
        elif command == "--help":
            print("""
🤖 Sistema Unificado de Produção de Conteúdo Educacional

MODOS DE USO:

1. MODO INTERATIVO (recomendado):
   python content_pipeline.py

2. LINHA DE COMANDO:
   python content_pipeline.py --complete video.mp4 [modulo] [aula]
   python content_pipeline.py --batch [pasta_videos] [modulo_inicial]
   python content_pipeline.py --youtube aula_diretorio
   python content_pipeline.py video.mp4  # compatibilidade

EXEMPLOS:
   python content_pipeline.py                                    # Menu interativo
   python content_pipeline.py --complete videos/aula01.mp4 1 1    # Processamento completo
   python content_pipeline.py --batch videos 1                   # Lote
   python content_pipeline.py --youtube modulo-01/aula-01-intro   # YouTube apenas

FUNCIONALIDADES:
   ✅ Transcrição com Groq Whisper
   ✅ Análise inteligente com Gemini
   ✅ Documentação automática (README, JSON)
   ✅ Legendas SRT (PT/EN/ES)
   ✅ Capítulos para YouTube
   ✅ Shorts automáticos
   ✅ Metadados SEO

VARIÁVEIS DE AMBIENTE:
   GROQ_API_KEY    - Obrigatória para transcrição
   GEMINI_API_KEY  - Opcional para análise IA e YouTube
            """)
            sys.exit(0)
        else:
            print(f"❌ Comando não reconhecido: {command}")
            print("Use --help para ver os comandos disponíveis")
            sys.exit(1)
    
    # Modo interativo (padrão)
    try:
        if not DEPENDENCIES_AVAILABLE:
            print("❌ Dependências não instaladas. Execute: ./instalar.sh")
            sys.exit(1)
            
        pipeline = UnifiedContentPipeline()
        menu = InteractiveMenu(pipeline)
        menu.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Sistema encerrado pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 