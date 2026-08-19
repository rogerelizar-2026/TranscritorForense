"""
Transcritor de Áudio Simplificado
Versão leve e eficiente para transcrição com identificação de falantes
"""

import os
import sys
import torch
import warnings
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Suprimir warnings desnecessários
warnings.filterwarnings("ignore")


class AudioTranscriber:
    """
    Transcritor de áudio simplificado com diarização e identificação de falantes.
    Foco em simplicidade, eficiência e menos erros.
    """
    
    def __init__(self, language: str = "pt", device: str = None):
        """
        Inicializa o transcritor.
        
        Args:
            language: Código do idioma ('pt', 'en', etc.)
            device: Dispositivo ('cuda' ou 'cpu'). Auto-detect se None.
        """
        self.language = language
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.diarizer = None
        self.transcriber = None
        self.speaker_classifier = None
        self.reference_embeddings: Dict[str, torch.Tensor] = {}
        self.speaker_map: Dict[str, str] = {}
        self._models_loaded = {"diarize": False, "transcribe": False, "identify": False}
        
        print(f"✅ Transcritor inicializado - Device: {self.device}")
    
    def _load_diarizer(self):
        """Carrega modelo de diarização lazy loading."""
        if not self._models_loaded["diarize"]:
            try:
                from pyannote.audio import Pipeline
                from huggingface_hub import login
                
                token = os.getenv("HUGGINGFACE_TOKEN", "")
                if token:
                    login(token=token)
                
                self.diarizer = Pipeline.from_pretrained(
                    "pyannote/speaker-diarization-3.1",
                    use_auth_token=token if token else None
                )
                self.diarizer.to(torch.device(self.device))
                self._models_loaded["diarize"] = True
                print("✅ Modelo de diarização carregado")
            except Exception as e:
                print(f"⚠️ Erro ao carregar diarização: {e}")
                raise
    
    def _load_transcriber(self):
        """Carrega modelo de transcrição lazy loading."""
        if not self._models_loaded["transcribe"]:
            try:
                import whisperx
                
                model_name = "base"  # Modelo leve e eficiente
                compute_type = "float16" if self.device == "cuda" else "float32"
                
                self.transcriber = whisperx.load_model(
                    model_name, 
                    self.device, 
                    compute_type=compute_type, 
                    language=self.language
                )
                
                self.align_model, self.metadata = whisperx.load_align_model(
                    language_code=self.language, 
                    device=self.device
                )
                self._models_loaded["transcribe"] = True
                print("✅ Modelo de transcrição carregado")
            except Exception as e:
                print(f"⚠️ Erro ao carregar transcrição: {e}")
                raise
    
    def _load_speaker_classifier(self):
        """Carrega classificador de falantes lazy loading."""
        if not self._models_loaded["identify"]:
            try:
                from speechbrain.inference.speaker import EncoderClassifier
                
                self.speaker_classifier = EncoderClassifier.from_hparams(
                    source="speechbrain/spkrec-ecapa-voxceleb",
                    savedir="models/speaker_classifier",
                    run_opts={"device": self.device}
                )
                self._models_loaded["identify"] = True
                print("✅ Classificador de falantes carregado")
            except Exception as e:
                print(f"⚠️ Erro ao carregar identificador: {e}")
                raise
    
    def diarize(self, audio_path: str, min_speakers: int = 1, max_speakers: int = 5) -> List[Dict]:
        """
        Realiza diarização do áudio (identifica segmentos por falante).
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            min_speakers: Número mínimo de falantes
            max_speakers: Número máximo de falantes
            
        Returns:
            Lista de segmentos com início, fim e ID do falante
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
        
        self._load_diarizer()
        
        diarization = self.diarizer(
            audio_path, 
            min_speakers=min_speakers, 
            max_speakers=max_speakers
        )
        
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            segments.append({
                "start": float(turn.start),
                "end": float(turn.end),
                "speaker": speaker,
                "text": "",
                "identified_as": None,
                "confidence": 0.0
            })
        
        return sorted(segments, key=lambda x: x["start"])
    
    def transcribe(self, audio_path: str) -> Tuple[str, List[Dict]]:
        """
        Transcreve o áudio com alinhamento temporal.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            
        Returns:
            Tupla com (texto completo, lista de segmentos transcritos)
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
        
        self._load_transcriber()
        
        # Transcrição inicial
        result = self.transcriber.transcribe(audio_path, batch_size=16)
        
        # Alinhamento fonético para precisão temporal
        aligned = whisperx.align(
            result["segments"],
            self.align_model,
            self.metadata,
            audio_path,
            self.device,
            return_char_alignments=False
        )
        
        return result.get("text", ""), aligned["segments"]
    
    def _extract_embedding(self, audio_path: str, start: float, end: float) -> Optional[torch.Tensor]:
        """Extrai embedding de voz de um segmento."""
        self._load_speaker_classifier()
        
        try:
            import torchaudio
            
            waveform, sample_rate = torchaudio.load(audio_path)
            
            # Corta segmento
            if start is not None and end is not None:
                start_sample = int(start * sample_rate)
                end_sample = int(end * sample_rate)
                waveform = waveform[:, start_sample:end_sample]
            
            # Verifica tamanho mínimo
            min_samples = sample_rate // 2  # 0.5 segundos
            if waveform.shape[1] < min_samples:
                return None
            
            # Extrai embedding
            embedding = self.speaker_classifier.encode_batch(waveform)
            return torch.nn.functional.normalize(embedding, p=2, dim=1).squeeze(0)
            
        except Exception as e:
            print(f"Erro ao extrair embedding: {e}")
            return None
    
    def register_reference(self, name: str, audio_path: str) -> bool:
        """
        Registra amostra de referência de um falante.
        
        Args:
            name: Nome do falante
            audio_path: Caminho para áudio de referência
            
        Returns:
            True se registrado com sucesso
        """
        if not os.path.exists(audio_path):
            print(f"Arquivo de referência não encontrado: {audio_path}")
            return False
        
        embedding = self._extract_embedding(audio_path, 0, None)
        if embedding is not None:
            self.reference_embeddings[name] = embedding
            print(f"✅ Referência registrada: {name}")
            return True
        
        print(f"❌ Falha ao extrair embedding de {name}")
        return False
    
    def identify_speaker(self, embedding: torch.Tensor, threshold: float = 0.75) -> Tuple[Optional[str], float]:
        """
        Identifica falante comparando com referências registradas.
        
        Args:
            embedding: Embedding do segmento
            threshold: Limiar de similaridade mínima
            
        Returns:
            Tupla com (nome do falante ou None, score de confiança)
        """
        if not self.reference_embeddings:
            return None, 0.0
        
        embedding = torch.nn.functional.normalize(embedding.unsqueeze(0), p=2, dim=1).squeeze(0)
        
        best_match, best_score = None, 0.0
        for name, ref_emb in self.reference_embeddings.items():
            similarity = torch.dot(embedding, ref_emb).item()
            if similarity > best_score:
                best_score = similarity
                best_match = name
        
        if best_score >= threshold:
            return best_match, best_score
        
        return None, best_score
    
    def process(self, audio_path: str, min_speakers: int = 1, max_speakers: int = 5, 
                identify: bool = True, threshold: float = 0.75) -> Dict:
        """
        Processa áudio completo: diariza, transcreve e identifica falantes.
        
        Args:
            audio_path: Caminho para o arquivo de áudio
            min_speakers: Número mínimo de falantes
            max_speakers: Número máximo de falantes
            identify: Se deve tentar identificar falantes
            threshold: Limiar para identificação
            
        Returns:
            Dicionário com resultados completos
        """
        print(f"\n🎙️ Processando: {audio_path}")
        print("-" * 50)
        
        if not os.path.exists(audio_path):
            return {"error": f"Arquivo não encontrado: {audio_path}"}
        
        try:
            # Step 1: Diarização
            print("📊 [1/3] Diarizando...")
            diarization = self.diarize(audio_path, min_speakers, max_speakers)
            print(f"   → {len(diarization)} segmentos encontrados")
            
            # Step 2: Transcrição
            print("📝 [2/3] Transcrevendo...")
            full_text, transcription_segments = self.transcribe(audio_path)
            print(f"   → {len(transcription_segments)} segmentos transcritos")
            
            # Step 3: Combina diarização com transcrição
            print("🔗 [3/3] Combinando resultados...")
            combined = self._combine_results(diarization, transcription_segments)
            
            # Step 4: Identificação (opcional)
            if identify and self.reference_embeddings:
                print("🎯 Identificando falantes...")
                for seg in combined:
                    emb = self._extract_embedding(audio_path, seg["start"], seg["end"])
                    if emb is not None:
                        name, conf = self.identify_speaker(emb, threshold)
                        seg["identified_as"] = name
                        seg["confidence"] = conf
            
            # Aplica mapeamento manual
            for seg in combined:
                if seg["speaker"] in self.speaker_map:
                    seg["identified_as"] = self.speaker_map[seg["speaker"]]
            
            speakers_found = set(seg["speaker"] for seg in combined)
            identified_count = sum(1 for seg in combined if seg["identified_as"])
            
            print("\n" + "=" * 50)
            print(f"✅ Processamento concluído!")
            print(f"   • Duração: {combined[-1]['end']:.1f}s" if combined else "   • Sem segmentos")
            print(f"   • Falantes: {len(speakers_found)}")
            print(f"   • Identificados: {identified_count}")
            print("=" * 50)
            
            return {
                "success": True,
                "audio_file": audio_path,
                "full_text": full_text,
                "segments": combined,
                "speakers": list(speakers_found),
                "metadata": {
                    "duration": combined[-1]["end"] if combined else 0,
                    "total_segments": len(combined),
                    "language": self.language,
                    "device": self.device,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"\n❌ Erro no processamento: {e}")
            return {"error": str(e), "audio_file": audio_path}
    
    def _combine_results(self, diarization: List[Dict], transcription: List[Dict]) -> List[Dict]:
        """Combina segmentos de diarização com texto transcrito."""
        combined = []
        
        for diag_seg in diarization:
            # Encontra transcrições que se sobrepõem
            overlapping_text = []
            for trans_seg in transcription:
                if (trans_seg.get("start", 0) <= diag_seg["end"] and 
                    trans_seg.get("end", 0) >= diag_seg["start"]):
                    text = trans_seg.get("text", "").strip()
                    if text:
                        overlapping_text.append(text)
            
            combined.append({
                "speaker": diag_seg["speaker"],
                "start": diag_seg["start"],
                "end": diag_seg["end"],
                "text": " ".join(overlapping_text) or "[sem áudio]",
                "identified_as": None,
                "confidence": 0.0
            })
        
        return combined
    
    def map_speaker(self, speaker_id: str, name: str):
        """Mapeia ID de falante para nome."""
        self.speaker_map[speaker_id] = name
        print(f"✅ Mapeado: {speaker_id} → {name}")
    
    def format_timestamp(self, seconds: float) -> str:
        """Formata segundos em MM:SS.mmm."""
        minutes = int(seconds // 60)
        secs = seconds % 60
        millis = int((secs % 1) * 1000)
        return f"{minutes:02d}:{int(secs):02d}.{millis:03d}"
    
    def save_report(self, results: Dict, output_dir: str = "output", 
                    formats: List[str] = None) -> List[str]:
        """
        Salva relatório em arquivos.
        
        Args:
            results: Resultados do processamento
            output_dir: Diretório de saída
            formats: Formatos desejados ['txt', 'md', 'html']
            
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        if formats is None:
            formats = ["txt"]
        
        os.makedirs(output_dir, exist_ok=True)
        files_created = []
        
        base_name = os.path.splitext(os.path.basename(results["audio_file"]))[0]
        
        for fmt in formats:
            try:
                if fmt == "txt":
                    content = self._generate_txt(results)
                    filepath = os.path.join(output_dir, f"{base_name}_transcricao.txt")
                
                elif fmt == "md":
                    content = self._generate_markdown(results)
                    filepath = os.path.join(output_dir, f"{base_name}_relatorio.md")
                
                elif fmt == "html":
                    content = self._generate_html(results)
                    filepath = os.path.join(output_dir, f"{base_name}_relatorio.html")
                
                else:
                    continue
                
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                
                files_created.append(filepath)
                print(f"📄 Gerado: {filepath}")
                
            except Exception as e:
                print(f"⚠️ Erro ao gerar {fmt}: {e}")
        
        return files_created
    
    def _generate_txt(self, results: Dict) -> str:
        """Gera relatório em texto simples."""
        lines = [
            "=" * 70,
            "TRANSCRIÇÃO DE ÁUDIO",
            "=" * 70,
            f"Arquivo: {results['audio_file']}",
            f"Data: {results['metadata']['timestamp']}",
            f"Duração: {results['metadata']['duration']:.1f}s",
            "-" * 70,
            ""
        ]
        
        current_speaker = None
        for seg in results["segments"]:
            speaker_name = seg["identified_as"] or seg["speaker"]
            timestamp = self.format_timestamp(seg["start"])
            
            if speaker_name != current_speaker:
                lines.append(f"\n[{timestamp}] {speaker_name}:")
                current_speaker = speaker_name
            
            lines.append(f"  {seg['text']}")
        
        lines.extend(["", "=" * 70])
        return "\n".join(lines)
    
    def _generate_markdown(self, results: Dict) -> str:
        """Gera relatório em Markdown."""
        lines = [
            "# Relatório de Transcrição\n",
            f"**Arquivo:** {results['audio_file']}  ",
            f"**Data:** {results['metadata']['timestamp']}  ",
            f"**Duração:** {results['metadata']['duration']:.1f}s  \n",
            "## Transcrição\n"
        ]
        
        current_speaker = None
        for seg in results["segments"]:
            speaker_name = seg["identified_as"] or seg["speaker"]
            timestamp = self.format_timestamp(seg["start"])
            
            if speaker_name != current_speaker:
                lines.append(f"\n**[{timestamp}] {speaker_name}:**")
                current_speaker = speaker_name
            
            lines.append(f"- {seg['text']}")
        
        return "\n".join(lines)
    
    def _generate_html(self, results: Dict) -> str:
        """Gera relatório em HTML."""
        html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Transcrição - {file}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }}
        .segment {{ margin: 10px 0; padding: 10px; border-left: 3px solid #3498db; }}
        .speaker {{ font-weight: bold; color: #2c3e50; }}
        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>TRANSCRIÇÃO DE ÁUDIO</h1>
        <p><strong>Arquivo:</strong> {file}</p>
        <p><strong>Duração:</strong> {duration:.1f}s</p>
    </div>
    <div class="transcript">
""".format(file=results['audio_file'], duration=results['metadata']['duration'])
        
        current_speaker = None
        for seg in results["segments"]:
            speaker_name = seg["identified_as"] or seg["speaker"]
            timestamp = self.format_timestamp(seg["start"])
            
            if speaker_name != current_speaker:
                html += f'<div class="segment"><span class="timestamp">[{timestamp}]</span> <span class="speaker">{speaker_name}:</span></div>\n'
                current_speaker = speaker_name
            
            html += f'<div class="segment">{seg["text"]}</div>\n'
        
        html += """    </div>
</body>
</html>"""
        return html


def main():
    """Função principal para uso via linha de comando."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Transcritor de Áudio Simplificado")
    parser.add_argument("audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("--min-speakers", type=int, default=1, help="Número mínimo de falantes")
    parser.add_argument("--max-speakers", type=int, default=5, help="Número máximo de falantes")
    parser.add_argument("--language", default="pt", help="Idioma (padrão: pt)")
    parser.add_argument("--device", choices=["cpu", "cuda"], default=None, help="Dispositivo")
    parser.add_argument("--output-dir", default="output", help="Diretório de saída")
    parser.add_argument("--reference", action="append", nargs=2, metavar=("NAME", "AUDIO"),
                       help="Amostra de referência (nome, caminho)")
    parser.add_argument("--no-identify", action="store_true", help="Desativa identificação")
    
    args = parser.parse_args()
    
    # Cria transcritor
    transcriber = AudioTranscriber(language=args.language, device=args.device)
    
    # Registra referências
    if args.reference:
        for name, path in args.reference:
            transcriber.register_reference(name, path)
    
    # Processa áudio
    results = transcriber.process(
        args.audio,
        min_speakers=args.min_speakers,
        max_speakers=args.max_speakers,
        identify=not args.no_identify
    )
    
    if "error" in results:
        print(f"\n❌ Erro: {results['error']}")
        sys.exit(1)
    
    # Salva relatórios
    files = transcriber.save_report(results, args.output_dir, formats=["txt", "md"])
    
    print(f"\n✅ Conclusão! Arquivos salvos em: {args.output_dir}/")
    for f in files:
        print(f"   - {f}")


if __name__ == "__main__":
    main()
