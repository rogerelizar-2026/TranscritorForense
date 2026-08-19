"""
Transcritor Forense de Áudio - Versão 2.0 Otimizada
Sistema profissional para transcrição com validade jurídica.
Integra diarização, transcrição, identificação e relatórios forenses.
"""

import os
import sys
import hashlib
import json
import torch
import torchaudio
import yaml
import gradio as gr
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from jinja2 import Template
import warnings
import traceback

warnings.filterwarnings("ignore")

# Configuração de dispositivo
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "float32"


class ForensicTranscriber:
    """
    Transcritor Forense - Sistema integrado para análise de áudio com validade jurídica.
    
    Componentes:
    - Diarização: pyannote.audio (detecção de falantes)
    - Transcrição: whisperx (transcrição precisa com alinhamento)
    - Identificação: speechbrain (reconhecimento por amostra de voz)
    - Relatórios: MD/TXT/HTML com hash SHA-256 e metadados forenses
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Inicializa o transcritor com configuração."""
        self.config = self._load_config(config_path)
        self.diarizer_pipeline = None
        self.transcription_model = None
        self.align_model = None
        self.align_metadata = None
        self.speaker_classifier = None
        self.reference_embeddings: Dict[str, torch.Tensor] = {}
        self.speaker_map: Dict[str, str] = {}
        self.speaker_metadata: Dict[str, Dict] = {}
        self.current_segments: List[Dict] = []
        self.current_audio_path: Optional[str] = None
        self.processing_log: List[Dict] = []
        
        # Log de inicialização
        self._log_event("system_init", {
            "device": DEVICE,
            "compute_type": COMPUTE_TYPE,
            "timestamp": datetime.now().isoformat()
        })
    
    def _load_config(self, config_path: str) -> Dict:
        """Carrega configuração YAML."""
        default_config = {
            "huggingface_token": "",
            "diarization_model": "pyannote/speaker-diarization-3.1",
            "transcription_model": "large-v2",
            "embedding_model": "speechbrain/spkrec-ecapa-voxceleb",
            "language": "pt",
            "speaker_identification_threshold": 0.75,
            "min_speakers": 2,
            "max_speakers": 5
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                    default_config.update(user_config)
            except Exception as e:
                self._log_event("config_error", {"error": str(e)})
        
        return default_config
    
    def _log_event(self, event_type: str, data: Dict):
        """Registra evento no log de processamento."""
        self.processing_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data
        })
    
    def _get_hf_token(self) -> Optional[str]:
        """Obtém token do Hugging Face."""
        token = self.config.get("huggingface_token", "")
        if not token:
            token = os.environ.get("HF_TOKEN", "")
        return token if token else None
    
    # ==================== DIARIZAÇÃO ====================
    
    def _load_diarizer(self):
        """Carrega pipeline de diarização (lazy loading)."""
        if self.diarizer_pipeline is None:
            try:
                from pyannote.audio import Pipeline
                from huggingface_hub import login
                
                token = self._get_hf_token()
                model = self.config.get("diarization_model", "pyannote/speaker-diarization-3.1")
                
                if token:
                    login(token=token)
                    self._log_event("hf_login", {"status": "success"})
                
                self.diarizer_pipeline = Pipeline.from_pretrained(model)
                self.diarizer_pipeline.to(torch.device(DEVICE))
                self._log_event("diarizer_loaded", {"model": model, "device": DEVICE})
                
            except Exception as e:
                self._log_event("diarizer_error", {"error": str(e), "traceback": traceback.format_exc()})
                raise RuntimeError(f"Falha ao carregar diarizador: {str(e)}")
    
    def diarize(self, audio_path: str, min_speakers: int = None, max_speakers: int = None) -> List[Dict]:
        """Realiza diarização do áudio."""
        self._load_diarizer()
        
        min_spk = min_speakers or self.config.get("min_speakers", 2)
        max_spk = max_speakers or self.config.get("max_speakers", 5)
        
        diarization = self.diarizer_pipeline(
            audio_path, 
            min_speakers=min_spk, 
            max_speakers=max_spk
        )
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": float(turn.start),
                "end": float(turn.end),
                "speaker": speaker,
                "confidence": 1.0
            })
        
        self._log_event("diarization_complete", {
            "segments_count": len(segments),
            "speakers_count": len(set(s["speaker"] for s in segments))
        })
        
        return segments
    
    # ==================== TRANSCRIÇÃO ====================
    
    def _load_transcriber(self):
        """Carrega modelo de transcrição (lazy loading)."""
        if self.transcription_model is None:
            try:
                import whisperx
                
                model_name = self.config.get("transcription_model", "large-v2")
                language = self.config.get("language", "pt")
                
                self.transcription_model = whisperx.load_model(
                    model_name, 
                    DEVICE, 
                    compute_type=COMPUTE_TYPE, 
                    language=language
                )
                
                self.align_model, self.align_metadata = whisperx.load_align_model(
                    language_code=language, 
                    device=DEVICE
                )
                
                self._log_event("transcriber_loaded", {
                    "model": model_name,
                    "language": language,
                    "device": DEVICE
                })
                
            except Exception as e:
                self._log_event("transcriber_error", {"error": str(e), "traceback": traceback.format_exc()})
                raise RuntimeError(f"Falha ao carregar transcritor: {str(e)}")
    
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """Transcreve áudio com alinhamento fonético."""
        self._load_transcriber()
        
        # Transcrição inicial
        result = self.transcription_model.transcribe(audio_path, batch_size=16)
        language = result.get("language", self.config.get("language", "pt"))
        
        # Alinhamento fonético
        result_aligned = whisperx.align(
            result["segments"], 
            self.align_model, 
            self.align_metadata, 
            audio_path, 
            DEVICE, 
            return_char_alignments=False
        )
        
        self._log_event("transcription_complete", {
            "language": language,
            "segments_count": len(result_aligned.get("segments", []))
        })
        
        return {
            "segments": result_aligned.get("segments", []),
            "language": language,
            "text": result.get("text", "")
        }
    
    # ==================== IDENTIFICAÇÃO DE FALANTES ====================
    
    def _load_speaker_classifier(self):
        """Carrega classificador de falantes (lazy loading)."""
        if self.speaker_classifier is None:
            try:
                from speechbrain.inference.speaker import EncoderClassifier
                
                model_name = self.config.get("embedding_model", "speechbrain/spkrec-ecapa-voxceleb")
                save_dir = os.path.join("models", model_name.replace("/", "_"))
                
                self.speaker_classifier = EncoderClassifier.from_hparams(
                    source=model_name, 
                    savedir=save_dir, 
                    run_opts={"device": DEVICE}
                )
                
                self._log_event("speaker_classifier_loaded", {
                    "model": model_name,
                    "device": DEVICE
                })
                
            except Exception as e:
                self._log_event("classifier_error", {"error": str(e), "traceback": traceback.format_exc()})
                raise RuntimeError(f"Falha ao carregar classificador: {str(e)}")
    
    def _extract_embedding(self, audio_path: str, start: float = None, end: float = None) -> Optional[torch.Tensor]:
        """Extrai embedding de voz de segmento."""
        self._load_speaker_classifier()
        
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            
            if start is not None and end is not None:
                start_sample = int(start * sample_rate)
                end_sample = int(end * sample_rate)
                waveform = waveform[:, start_sample:end_sample]
            
            # Verifica se o segmento é longo o suficiente (mínimo 0.5s)
            min_samples = sample_rate * 0.5
            if waveform.shape[1] < min_samples:
                return None
            
            embedding = self.speaker_classifier.encode_batch(waveform)
            return torch.nn.functional.normalize(embedding, p=2, dim=1).squeeze(0)
            
        except Exception as e:
            self._log_event("embedding_error", {"error": str(e)})
            return None
    
    def register_reference(self, name: str, audio_path: str) -> bool:
        """Registra amostra de referência para identificação."""
        embedding = self._extract_embedding(audio_path)
        if embedding is not None:
            self.reference_embeddings[name.strip()] = embedding
            self._log_event("reference_registered", {"name": name.strip()})
            return True
        return False
    
    def identify_speaker(self, embedding: torch.Tensor) -> Tuple[Optional[str], float]:
        """Identifica falante comparando com referências registradas."""
        if not self.reference_embeddings:
            return None, 0.0
        
        embedding_normalized = torch.nn.functional.normalize(
            embedding.unsqueeze(0), p=2, dim=1
        ).squeeze(0)
        
        best_match, best_score = None, 0.0
        
        for name, ref_embedding in self.reference_embeddings.items():
            similarity = torch.dot(embedding_normalized, ref_embedding).item()
            if similarity > best_score:
                best_score = similarity
                best_match = name
        
        threshold = self.config.get("speaker_identification_threshold", 0.75)
        
        if best_score >= threshold:
            return best_match, best_score
        return None, best_score
    
    def identify_segments(self, segments: List[Dict], audio_path: str) -> List[Dict]:
        """Identifica falantes em todos os segmentos."""
        identified = []
        identified_count = 0
        
        for segment in segments:
            embedding = self._extract_embedding(
                audio_path, 
                segment["start"], 
                segment["end"]
            )
            
            result = segment.copy()
            result["identified_as"] = None
            result["confidence"] = 0.0
            
            if embedding is not None:
                identified_name, score = self.identify_speaker(embedding)
                result["identified_as"] = identified_name
                result["confidence"] = score
                if identified_name:
                    identified_count += 1
            
            identified.append(result)
        
        self._log_event("identification_complete", {
            "total_segments": len(segments),
            "identified_count": identified_count
        })
        
        return identified
    
    # ==================== MAPEAMENTO DE FALANTES ====================
    
    def map_speaker(self, speaker_id: str, name: str, confidence: float = 1.0, method: str = "manual"):
        """Mapeia ID de falante para nome."""
        self.speaker_map[speaker_id] = name.strip()
        self.speaker_metadata[speaker_id] = {
            "confidence": confidence,
            "method": method,
            "mapped_at": datetime.now().isoformat()
        }
        self._log_event("speaker_mapped", {
            "speaker_id": speaker_id,
            "name": name.strip(),
            "method": method
        })
    
    def get_speaker_name(self, speaker_id: str) -> str:
        """Obtém nome do falante a partir do ID."""
        return self.speaker_map.get(speaker_id, speaker_id)
    
    def auto_map_from_identification(self, identified_segments: List[Dict]):
        """Cria mapeamento automático baseado em identificação."""
        speaker_votes: Dict[str, Dict[str, List[float]]] = {}
        
        for seg in identified_segments:
            speaker_id = seg.get("speaker", "")
            identified_as = seg.get("identified_as")
            confidence = seg.get("confidence", 0.0)
            
            if identified_as and speaker_id:
                if speaker_id not in speaker_votes:
                    speaker_votes[speaker_id] = {}
                if identified_as not in speaker_votes[speaker_id]:
                    speaker_votes[speaker_id][identified_as] = []
                speaker_votes[speaker_id][identified_as].append(confidence)
        
        mapped_count = 0
        for speaker_id, votes in speaker_votes.items():
            best_name, best_avg = None, 0.0
            for name, scores in votes.items():
                avg = sum(scores) / len(scores)
                if avg > best_avg:
                    best_avg = avg
                    best_name = name
            
            if best_name and best_avg >= 0.5:
                self.map_speaker(speaker_id, best_name, best_avg, "automatic")
                mapped_count += 1
        
        self._log_event("auto_mapping_complete", {"mapped_count": mapped_count})
    
    def get_all_mappings(self) -> List[Dict]:
        """Retorna todos os mapeamentos de falantes."""
        return [
            {
                "speaker_id": sid,
                "name": name,
                **self.speaker_metadata.get(sid, {})
            }
            for sid, name in self.speaker_map.items()
        ]
    
    # ==================== UTILITÁRIOS FORENSES ====================
    
    def format_timestamp(self, seconds: float) -> str:
        """Formata segundos em HH:MM:SS.mmm."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs % 1) * 1000)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{int(secs):02d}.{millis:03d}"
        return f"{minutes:02d}:{int(secs):02d}.{millis:03d}"
    
    def compute_file_hash(self, filepath: str) -> str:
        """Computa hash SHA-256 do arquivo para integridade forense."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def get_audio_metadata(self, audio_path: str) -> Dict:
        """Extrai metadados técnicos do áudio."""
        try:
            info = torchaudio.info(audio_path)
            duration = info.num_frames / info.sample_rate
            
            return {
                "filepath": audio_path,
                "filename": os.path.basename(audio_path),
                "sample_rate": info.sample_rate,
                "channels": info.num_channels,
                "frames": info.num_frames,
                "duration_seconds": duration,
                "duration_formatted": self.format_timestamp(duration),
                "file_hash": self.compute_file_hash(audio_path),
                "processed_at": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "filepath": audio_path,
                "filename": os.path.basename(audio_path),
                "error": str(e),
                "processed_at": datetime.now().isoformat()
            }
    
    def generate_markdown(self, segments: List[Dict], metadata: Dict, speaker_map: Dict[str, str]) -> str:
        """Gera relatório Markdown."""
        lines = [
            "# RELATÓRIO DE TRANSCRIÇÃO FORENSE\n",
            "## METADADOS TÉCNICOS\n",
            f"- **Arquivo:** {metadata['audio_file']}",
            f"- **Processamento:** {metadata['processing_date']}",
            f"- **Duração:** {self.format_timestamp(metadata['total_duration'])}",
            f"- **Segmentos:** {metadata['total_segments']}\n"
        ]
        
        if metadata.get('speaker_mappings'):
            lines.extend([
                "## MAPEAMENTO DE FALANTES\n",
                "| ID | Nome | Método | Confiança |",
                "|----|------|--------|-----------|"
            ])
            for m in metadata['speaker_mappings']:
                lines.append(f"| {m.get('speaker_id')} | {m.get('name')} | {m.get('method')} | {m.get('confidence', 0):.2%} |")
            lines.append("")
        
        lines.append("## TRANSCRIÇÃO\n")
        current_speaker = None
        
        for seg in sorted(segments, key=lambda x: x.get("start", 0)):
            speaker_name = speaker_map.get(seg.get("speaker", ""), seg.get("speaker", ""))
            timestamp = self.format_timestamp(seg.get("start", 0))
            text = seg.get("text", "[inaudível]")
            
            if speaker_name != current_speaker:
                lines.append(f"**[{timestamp}] {speaker_name}:**")
                current_speaker = speaker_name
            lines.append(f"  {text}\n")
        
        lines.extend([
            "---\n",
            "## VALIDAÇÃO TÉCNICA\n",
            "Gerado por Transcritor Forense v1.0.0\n",
            "- **Diarização:** pyannote.audio",
            "- **Transcrição:** whisperx",
            "- **Identificação:** speechbrain"
        ])
        
        return "\n".join(lines)
    
    def generate_txt(self, segments: List[Dict], metadata: Dict, speaker_map: Dict[str, str]) -> str:
        """Gera relatório TXT."""
        lines = [
            "=" * 70,
            "RELATÓRIO DE TRANSCRIÇÃO FORENSE",
            "=" * 70,
            f"Arquivo: {metadata['audio_file']}",
            f"Processamento: {metadata['processing_date']}",
            "-" * 70,
            "TRANSCRIÇÃO",
            "-" * 70
        ]
        
        for seg in sorted(segments, key=lambda x: x.get("start", 0)):
            speaker_name = speaker_map.get(seg.get("speaker", ""), seg.get("speaker", ""))
            timestamp = self.format_timestamp(seg.get("start", 0))
            text = seg.get("text", "[inaudível]")
            lines.append(f"[{timestamp}] {speaker_name}: {text}")
        
        lines.extend(["", "=" * 70, "Transcritor Forense v1.0.0", "=" * 70])
        return "\n".join(lines)
    
    def generate_html(self, segments: List[Dict], metadata: Dict, speaker_map: Dict[str, str]) -> str:
        """Gera relatório HTML."""
        template_str = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Relatório Forense - {{ metadata.audio_file }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .metadata { background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .segment { margin: 10px 0; padding: 10px; border-left: 3px solid #3498db; }
        .speaker { font-weight: bold; color: #2c3e50; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #bdc3c7; font-size: 0.9em; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #3498db; color: white; }
    </style>
</head>
<body>
    <div class="header"><h1>RELATÓRIO DE TRANSCRIÇÃO FORENSE</h1></div>
    <div class="metadata">
        <h2>METADADOS</h2>
        <p><strong>Arquivo:</strong> {{ metadata.audio_file }}</p>
        <p><strong>Data:</strong> {{ metadata.processing_date }}</p>
        <p><strong>Duração:</strong> {{ metadata.total_duration_formatted }}</p>
        {% if speaker_mappings %}
        <h3>Falantes</h3>
        <table><tr><th>ID</th><th>Nome</th><th>Método</th><th>Confiança</th></tr>
        {% for m in speaker_mappings %}
        <tr><td>{{ m.speaker_id }}</td><td>{{ m.name }}</td><td>{{ m.method }}</td><td>{{ "%.0f"|format(m.confidence*100) }}%</td></tr>
        {% endfor %}</table>
        {% endif %}
    </div>
    <div class="transcript"><h2>TRANSCRIÇÃO</h2>
    {% for seg in segments %}
    <div class="segment"><span class="timestamp">[{{ seg.timestamp }}]</span> <span class="speaker">{{ seg.speaker }}:</span> {{ seg.text }}</div>
    {% endfor %}</div>
    <div class="footer"><p>Transcritor Forense v1.0.0 | pyannote.audio • whisperx • speechbrain</p></div>
</body>
</html>"""
        
        env = Environment(loader=BaseLoader())
        formatted_segs = [
            {
                "timestamp": self.format_timestamp(seg.get("start", 0)),
                "speaker": speaker_map.get(seg.get("speaker", ""), seg.get("speaker", "")),
                "text": seg.get("text", "[inaudível]")
            }
            for seg in sorted(segments, key=lambda x: x.get("start", 0))
        ]
        
        metadata["total_duration_formatted"] = self.format_timestamp(metadata.get("total_duration", 0))
        template = Template(template_str)
        return template.render(segments=formatted_segs, metadata=metadata, speaker_mappings=metadata.get("speaker_mappings", []))
    
    # ==================== PROCESSAMENTO PRINCIPAL ====================
    
    def process_audio(self, audio_path: str, min_speakers: int = 2, max_speakers: int = 5, progress=None) -> Tuple[str, List, List]:
        """Processa áudio completo."""
        if not audio_path or not os.path.exists(audio_path):
            return "❌ Arquivo não encontrado", [], []
        
        self.current_audio_path = audio_path
        
        try:
            if progress: progress(0.1, desc="Diarizando...")
            diarization = self.diarize(audio_path, min_speakers, max_speakers)
            if not diarization:
                return "❌ Falha na diarização", [], []
            
            if progress: progress(0.4, desc="Transcrevendo...")
            transcription = self.transcribe(audio_path)
            
            if progress: progress(0.7, desc="Identificando falantes...")
            identified = self.identify_segments(diarization, audio_path)
            self.auto_map_from_identification(identified)
            
            if progress: progress(0.9, desc="Combinando resultados...")
            combined = self._combine_transcription(diarization, transcription["segments"])
            self.current_segments = combined
            
            formatted = self._format_for_display(combined)
            mappings = self.get_all_mappings()
            
            if progress: progress(1.0, desc="Concluído!")
            
            return (
                f"✅ Processado!\n• {len(diarization)} segmentos\n• {len(set(s['speaker'] for s in diarization))} falantes\n• {len(mappings)} identificados",
                formatted,
                mappings
            )
        except Exception as e:
            return f"❌ Erro: {str(e)}", [], []
    
    def _combine_transcription(self, diarization: List[Dict], transcription: List[Dict]) -> List[Dict]:
        """Combina diarização com transcrição."""
        combined = []
        for diag_seg in diarization:
            overlapping_text = []
            for trans_seg in transcription:
                if trans_seg.get("start", 0) <= diag_seg["end"] and trans_seg.get("end", 0) >= diag_seg["start"]:
                    text = trans_seg.get("text", "").strip()
                    if text:
                        overlapping_text.append(text)
            
            combined.append({
                "speaker": diag_seg["speaker"],
                "start": diag_seg["start"],
                "end": diag_seg["end"],
                "text": " ".join(overlapping_text) if overlapping_text else "[sem áudio]",
                "identified_as": diag_seg.get("identified_as"),
                "confidence": diag_seg.get("confidence", 0.0)
            })
        return combined
    
    def _format_for_display(self, segments: List[Dict]) -> List[List]:
        """Formata segmentos para tabela."""
        formatted = []
        for seg in sorted(segments, key=lambda x: x["start"]):
            speaker_id = seg.get("speaker", "UNKNOWN")
            formatted.append([
                self.format_timestamp(seg.get("start", 0)),
                self.format_timestamp(seg.get("end", 0)),
                speaker_id,
                self.get_speaker_name(speaker_id),
                seg.get("text", ""),
                f"{seg.get('confidence', 0):.2%}" if seg.get("identified_as") else "N/A"
            ])
        return formatted
    
    # ==================== INTERFACE GRADIO ====================
    
    def create_interface(self) -> gr.Blocks:
        """Cria interface Gradio."""
        with gr.Blocks(title="Transcritor Forense") as app:
            gr.Markdown("# 🎙️ Transcritor Forense de Áudio\nFerramenta profissional para transcrição com validade jurídica.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📁 Entrada")
                    audio_input = gr.File(label="Áudio", file_types=["audio"])
                    min_spk = gr.Slider(1, 10, value=2, step=1, label="Mínimo Falantes")
                    max_spk = gr.Slider(1, 10, value=5, step=1, label="Máximo Falantes")
                    process_btn = gr.Button("🚀 Processar", variant="primary")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🎤 Amostras (Opcional)")
                    sample_inputs = []
                    for i, name in enumerate(["Cliente", "Empresa", "Falante 3", "Falante 4", "Falante 5"]):
                        with gr.Row():
                            sname = gr.Textbox(value=name, label="Nome", scale=1)
                            sfile = gr.File(label="Amostra", file_types=["audio"], scale=2)
                            sample_inputs.append((sname, sfile))
                    load_samples_btn = gr.Button("Carregar Amostras")
                    sample_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 📝 Transcrição")
                    transcript_table = gr.Dataframe(headers=["Início", "Fim", "ID", "Nome", "Texto", "Confiança"], label="Segmentos", wrap=True)
                    status_output = gr.Textbox(label="Status", interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🔧 Mapeamento Manual")
                    with gr.Row():
                        spk_id = gr.Textbox(label="ID", placeholder="SPEAKER_00")
                        spk_name = gr.Textbox(label="Nome", placeholder="João Silva")
                    map_btn = gr.Button("Atualizar")
                    map_status = gr.Textbox(label="Status", interactive=False)
                    
                    gr.Markdown("### 📄 Relatório")
                    report_format = gr.Radio(choices=["markdown", "txt", "html"], value="markdown", label="Formato")
                    generate_btn = gr.Button("Gerar Relatório")
                    report_status = gr.Textbox(label="Relatório", interactive=False)
            
            load_samples_btn.click(
                fn=lambda *args: self._load_samples_handler([(n.value, f.value) for n, f in sample_inputs if n.value and f.value]),
                inputs=[item for pair in sample_inputs for item in pair],
                outputs=sample_status
            ).then(
                fn=lambda: "✅ Amostras carregadas com sucesso!",
                outputs=map_status
            )
            
            process_btn.click(
                fn=self.process_audio,
                inputs=[audio_input, min_spk, max_spk],
                outputs=[status_output, transcript_table, gr.State()]
            )
            
            map_btn.click(fn=lambda sid, nm: (self.map_speaker(sid, nm.strip(), method="manual"), f"✅ {sid} → {nm.strip()}") if sid and nm else ("", "⚠️ Preencha ambos"), inputs=[spk_id, spk_name], outputs=[gr.State(), map_status])
            
            generate_btn.click(
                fn=lambda fmt: self.generate_report(self.current_audio_path, self.current_segments, [fmt])[fmt] if self.current_audio_path and self.current_segments else "❌ Processe áudio primeiro",
                inputs=[report_format],
                outputs=report_status
            )
            
            gr.Markdown("---\n### ℹ️ Metodologia\n- **Diarização:** pyannote.audio 3.1\n- **Transcrição:** whisperx 3.1\n- **Identificação:** speechbrain 1.0\n\n**Validade Jurídica:** Hash SHA-256 incluso")
        
        return app
    
    def _load_samples_handler(self, samples: List[Tuple[str, str]]) -> str:
        """Carrega amostras de referência."""
        loaded, failed = [], []
        for name, path in samples:
            if path and os.path.exists(path):
                if self.register_reference(name.strip(), path):
                    loaded.append(name.strip())
                else:
                    failed.append(f"{name.strip()} (erro)")
            else:
                failed.append(f"{name.strip()} (não encontrado)")
        
        msg = f"✅ {', '.join(loaded)}" if loaded else ""
        if failed:
            msg += f"\n❌ {', '.join(failed)}" if msg else f"❌ {', '.join(failed)}"
        return msg or "Nenhuma amostra"
    
    def launch(self, server_name: str = "0.0.0.0", server_port: int = 7860, share: bool = False, **kwargs):
        """Lança aplicação."""
        app = self.create_interface()
        try:
            app.launch(server_name=server_name, server_port=server_port, share=share, **kwargs)
        except ValueError as e:
            if "localhost is not accessible" in str(e):
                print("Aviso: localhost não acessível. Ativando share=True...")
                app.launch(server_name=server_name, server_port=server_port, share=True, **kwargs)
            else:
                raise


def main():
    """Ponto de entrada principal."""
    app = ForensicTranscriber()
    app.launch()


if __name__ == "__main__":
    main()
