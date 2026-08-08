"""
Transcritor Forense de Áudio - Módulo Único Simplificado
Integra diarização, transcrição, identificação e formatação em uma solução coesa.
"""

import os
import hashlib
import torch
import torchaudio
import yaml
import gradio as gr
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from jinja2 import Environment, BaseLoader
import warnings

warnings.filterwarnings("ignore", category=UserWarning)


class ForensicTranscriber:
    """
    Classe única que integra todos os componentes do transcritor forense.
    
    Funcionalidades:
    - Diarização acústica (pyannote.audio)
    - Transcrição precisa (whisperx)
    - Identificação por amostras (speechbrain)
    - Geração de relatórios forenses (MD/TXT/HTML)
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Inicializa com configuração."""
        self.config = self._load_config(config_path)
        self.diarizer_pipeline = None
        self.transcription_model = None
        self.align_model = None
        self.speaker_classifier = None
        self.reference_embeddings: Dict[str, torch.Tensor] = {}
        self.speaker_map: Dict[str, str] = {}
        self.speaker_metadata: Dict[str, Dict] = {}
        self.current_segments = []
        self.current_audio_path = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Carrega configuração YAML."""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}
    
    # ==================== DIARIZAÇÃO ====================
    
    def _load_diarizer(self):
        """Carrega pipeline de diarização."""
        if self.diarizer_pipeline is None:
            from pyannote.audio import Pipeline
            token = self.config.get("huggingface_token", "")
            model = self.config.get("diarization_model", "pyannote/speaker-diarization-3.1")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Usa token (parâmetro correto para versões recentes do pyannote)
            if token:
                self.diarizer_pipeline = Pipeline.from_pretrained(model, token=token)
            else:
                self.diarizer_pipeline = Pipeline.from_pretrained(model)
            
            self.diarizer_pipeline.to(torch.device(device))
    def diarize(self, audio_path: str, min_speakers: int = 2, max_speakers: int = 5) -> List[Dict]:
        """Realiza diarização do áudio."""
        self._load_diarizer()
        diarization = self.diarizer_pipeline(audio_path, min_speakers=min_speakers, max_speakers=max_speakers)
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker,
                "confidence": 1.0
            })
        return segments
    
    # ==================== TRANSCRIÇÃO ====================
    
    def _load_transcriber(self):
        """Carrega modelo de transcrição."""
        if self.transcription_model is None:
            import whisperx
            model_name = self.config.get("transcription_model", "large-v2")
            language = self.config.get("language", "pt")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "float32"
            
            self.transcription_model = whisperx.load_model(model_name, device, compute_type=compute_type, language=language)
            self.align_model, self.metadata = whisperx.load_align_model(language_code=language, device=device)
    
    def transcribe(self, audio_path: str) -> Dict[str, Any]:
        """Transcreve áudio com alinhamento fonético."""
        self._load_transcriber()
        result = self.transcription_model.transcribe(audio_path, batch_size=16)
        language = result.get("language", self.config.get("language", "pt"))
        
        result_aligned = whisperx.align(
            result["segments"], self.align_model, self.metadata, audio_path, 
            "cuda" if torch.cuda.is_available() else "cpu", return_char_alignments=False
        )
        
        return {"segments": result_aligned["segments"], "language": language, "text": result.get("text", "")}
    
    # ==================== IDENTIFICAÇÃO ====================
    
    def _load_speaker_classifier(self):
        """Carrega classificador de falantes."""
        if self.speaker_classifier is None:
            from speechbrain.inference.speaker import EncoderClassifier
            model_name = self.config.get("embedding_model", "speechbrain/spkrec-ecapa-voxceleb")
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.speaker_classifier = EncoderClassifier.from_hparams(
                source=model_name, savedir=os.path.join("models", model_name.replace("/", "_")), run_opts={"device": device}
            )
    
    def _extract_embedding(self, audio_path: str, start: float = None, end: float = None) -> Optional[torch.Tensor]:
        """Extrai embedding de voz de segmento."""
        self._load_speaker_classifier()
        try:
            waveform, sample_rate = torchaudio.load(audio_path)
            if start is not None and end is not None:
                waveform = waveform[:, int(start * sample_rate):int(end * sample_rate)]
            
            if waveform.shape[1] < sample_rate * 0.5:
                return None
            
            embedding = self.speaker_classifier.encode_batch(waveform)
            return torch.nn.functional.normalize(embedding, p=2, dim=1).squeeze(0)
        except Exception as e:
            print(f"Erro ao extrair embedding: {e}")
            return None
    
    def register_reference(self, name: str, audio_path: str) -> bool:
        """Registra amostra de referência."""
        embedding = self._extract_embedding(audio_path)
        if embedding is not None:
            self.reference_embeddings[name] = embedding
            return True
        return False
    
    def identify_speaker(self, embedding: torch.Tensor) -> Tuple[Optional[str], float]:
        """Identifica falante comparando com referências."""
        if not self.reference_embeddings:
            return None, 0.0
        
        embedding = torch.nn.functional.normalize(embedding.unsqueeze(0), p=2, dim=1).squeeze(0)
        best_match, best_score = None, 0.0
        
        for name, ref_embedding in self.reference_embeddings.items():
            similarity = torch.dot(embedding, ref_embedding).item()
            if similarity > best_score:
                best_score = similarity
                best_match = name
        
        threshold = self.config.get("speaker_identification_threshold", 0.75)
        return (best_match, best_score) if best_score >= threshold else (None, best_score)
    
    def identify_segments(self, segments: List[Dict], audio_path: str) -> List[Dict]:
        """Identifica falantes em segmentos."""
        identified = []
        for segment in segments:
            embedding = self._extract_embedding(audio_path, segment["start"], segment["end"])
            result = segment.copy()
            result["identified_as"] = None
            result["confidence"] = 0.0
            
            if embedding is not None:
                identified_name, score = self.identify_speaker(embedding)
                result["identified_as"] = identified_name
                result["confidence"] = score
            
            identified.append(result)
        return identified
    
    # ==================== MAPEAMENTO ====================
    
    def map_speaker(self, speaker_id: str, name: str, confidence: float = 1.0, method: str = "manual"):
        """Mapeia ID para nome."""
        self.speaker_map[speaker_id] = name
        self.speaker_metadata[speaker_id] = {"confidence": confidence, "method": method}
    
    def get_speaker_name(self, speaker_id: str) -> str:
        """Obtém nome do falante."""
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
        
        for speaker_id, votes in speaker_votes.items():
            best_name, best_avg = None, 0.0
            for name, scores in votes.items():
                avg = sum(scores) / len(scores)
                if avg > best_avg:
                    best_avg = avg
                    best_name = name
            
            if best_name and best_avg >= 0.5:
                self.map_speaker(speaker_id, best_name, best_avg, "automatic")
    
    def get_all_mappings(self) -> List[Dict]:
        """Retorna todos os mapeamentos."""
        return [
            {"speaker_id": sid, "name": name, **self.speaker_metadata.get(sid, {})}
            for sid, name in self.speaker_map.items()
        ]
    
    # ==================== FORMATAÇÃO ====================
    
    def format_timestamp(self, seconds: float) -> str:
        """Formata segundos em HH:MM:SS.mmm."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs % 1) * 1000)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{int(secs):02d}.{millis:03d}"
        return f"{minutes:02d}:{int(secs):02d}.{millis:03d}"
    
    def compute_file_hash(self, file_path: str, algorithm: str = "sha256") -> str:
        """Calcula hash do arquivo."""
        hash_func = getattr(hashlib, algorithm)()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    
    def generate_markdown(self, segments: List[Dict], metadata: Dict, speaker_map: Dict[str, str]) -> str:
        """Gera relatório Markdown."""
        lines = [
            "# RELATÓRIO DE TRANSCRIÇÃO FORENSE\n",
            "## METADADOS TÉCNICOS\n",
            f"- **Arquivo:** {metadata['audio_file']}",
            f"- **Hash SHA-256:** `{metadata['audio_hash_sha256']}`",
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
        
        content = "\n".join(lines)
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        lines.extend(["\n### Hash do Conteúdo\n", f"`{content_hash}`"])
        return "\n".join(lines)
    
    def generate_txt(self, segments: List[Dict], metadata: Dict, speaker_map: Dict[str, str]) -> str:
        """Gera relatório TXT."""
        lines = [
            "=" * 70,
            "RELATÓRIO DE TRANSCRIÇÃO FORENSE",
            "=" * 70,
            f"Arquivo: {metadata['audio_file']}",
            f"Hash: {metadata['audio_hash_sha256']}",
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
        .hash { font-family: monospace; background: #f4f4f4; padding: 2px 5px; }
    </style>
</head>
<body>
    <div class="header"><h1>RELATÓRIO DE TRANSCRIÇÃO FORENSE</h1></div>
    <div class="metadata">
        <h2>METADADOS</h2>
        <p><strong>Arquivo:</strong> {{ metadata.audio_file }}</p>
        <p><strong>Hash:</strong> <span class="hash">{{ metadata.audio_hash_sha256 }}</span></p>
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
    <div class="footer"><p>Transcritor Forense v1.0.0 | pyannote.audio • whisperx • speechbrain</p><p>Hash: <span class="hash">{{ content_hash }}</span></p></div>
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
        template = env.from_string(template_str)
        html = template.render(segments=formatted_segs, metadata=metadata, speaker_mappings=metadata.get("speaker_mappings", []), content_hash="")
        content_hash = hashlib.sha256(html.encode()).hexdigest()
        return template.render(segments=formatted_segs, metadata=metadata, speaker_mappings=metadata.get("speaker_mappings", []), content_hash=content_hash)
    
    def generate_report(self, audio_path: str, segments: List[Dict], formats: List[str] = None) -> Dict[str, str]:
        """Gera relatório nos formatos especificados."""
        if formats is None:
            formats = ["markdown", "txt", "html"]
        
        output_dir = self.config.get("output_dir", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        speaker_map = {m["speaker_id"]: m["name"] for m in self.get_all_mappings()}
        metadata = {
            "audio_file": os.path.basename(audio_path),
            "audio_path": os.path.abspath(audio_path),
            "audio_hash_sha256": self.compute_file_hash(audio_path),
            "processing_date": datetime.now().isoformat(),
            "total_duration": max(seg.get("end", 0) for seg in segments) if segments else 0,
            "total_segments": len(segments),
            "speaker_mappings": self.get_all_mappings()
        }
        
        generators = {
            "markdown": lambda: self.generate_markdown(segments, metadata, speaker_map),
            "txt": lambda: self.generate_txt(segments, metadata, speaker_map),
            "html": lambda: self.generate_html(segments, metadata, speaker_map)
        }
        
        generated = {}
        for fmt in formats:
            if fmt in generators:
                content = generators[fmt]()
                ext = {"markdown": ".md", "txt": ".txt", "html": ".html"}[fmt]
                filename = f"forense_{os.path.splitext(os.path.basename(audio_path))[0]}{ext}"
                filepath = os.path.join(output_dir, filename)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                generated[fmt] = filepath
        
        return generated
    
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
