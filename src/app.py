"""
Aplicação Principal - Interface Gradio
Interface web local para transcrição forense de áudio
"""

import os
import yaml
import gradio as gr
from typing import Dict, List, Any, Optional
from datetime import datetime

from .diarizer import Diarizer
from .transcriber import Transcriber
from .speaker_identifier import SpeakerIdentifier
from .speaker_mapper import SpeakerMapper
from .forensic_formatter import ForensicFormatter


class ForensicTranscriberApp:
    """
    Aplicação completa de transcrição forense
    
    Integra todos os módulos em uma interface unificada.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Inicializa a aplicação com configuração
        
        Args:
            config_path: Caminho para arquivo de configuração YAML
        """
        self.config = self._load_config(config_path)
        
        # Inicializa componentes
        self.diarizer = Diarizer(
            huggingface_token=self.config.get("huggingface_token", ""),
            model_name=self.config.get("diarization_model", "pyannote/speaker-diarization-3.1")
        )
        
        self.transcriber = Transcriber(
            model_name=self.config.get("transcription_model", "large-v2"),
            language=self.config.get("language", "pt")
        )
        
        self.speaker_identifier = SpeakerIdentifier(
            model_name=self.config.get("embedding_model", "speechbrain/spkrec-ecapa-voxceleb"),
            threshold=self.config.get("speaker_identification_threshold", 0.75)
        )
        
        self.speaker_mapper = SpeakerMapper()
        self.formatter = ForensicFormatter(
            output_dir=self.config.get("output_dir", "output"),
            templates_dir="templates"
        )
        
        self.current_audio_path = None
        self.current_segments = []
        self.current_transcription = None
        
    def _load_config(self, config_path: str) -> Dict:
        """Carrega configuração do YAML"""
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {}
    
    def load_reference_samples(self, sample_files: List[str]) -> str:
        """
        Carrega amostras de referência para identificação
        
        Args:
            sample_files: Lista de tuplas (nome, caminho_do_arquivo)
            
        Returns:
            Mensagem de status
        """
        loaded = []
        failed = []
        
        for name, path in sample_files:
            if path and os.path.exists(path):
                if self.speaker_identifier.register_reference(name.strip(), path):
                    loaded.append(name.strip())
                else:
                    failed.append(f"{name.strip()} (erro ao extrair embedding)")
            else:
                failed.append(f"{name.strip()} (arquivo não encontrado)")
        
        msg = f"✅ Carregados: {', '.join(loaded)}" if loaded else ""
        if failed:
            msg += f"\n❌ Falharam: {', '.join(failed)}" if msg else f"❌ Falharam: {', '.join(failed)}"
        
        return msg or "Nenhuma amostra fornecida"
    
    def process_audio(self, audio_path: str, min_speakers: int = 2,
                     max_speakers: int = 5, progress=gr.Progress()) -> tuple:
        """
        Processa áudio completo (diarização + transcrição + identificação)
        
        Args:
            audio_path: Caminho para arquivo de áudio
            min_speakers: Número mínimo de falantes
            max_speakers: Número máximo de falantes
            progress: Barra de progresso do Gradio
            
        Returns:
            Tupla (mensagem_status, segmentos_formatados, mapeamentos)
        """
        if not audio_path or not os.path.exists(audio_path):
            return "❌ Arquivo de áudio não encontrado", [], []
        
        self.current_audio_path = audio_path
        
        try:
            # Passo 1: Diarização
            progress(0.1, desc="Realizando diarização...")
            diarization_segments = self.diarizer.diarize(
                audio_path, 
                min_speakers=min_speakers,
                max_speakers=max_speakers
            )
            
            if not diarization_segments:
                return "❌ Falha na diarização", [], []
            
            # Passo 2: Transcrição
            progress(0.4, desc="Transcrevendo áudio...")
            transcription = self.transcriber.transcribe(audio_path)
            self.current_transcription = transcription
            
            # Passo 3: Identificação por amostras (se disponíveis)
            progress(0.7, desc="Identificando falantes...")
            identified_segments = self.speaker_identifier.identify_segments(
                diarization_segments,
                audio_path
            )
            
            # Passo 4: Mapeamento automático
            self.speaker_mapper.auto_map_from_identification(identified_segments)
            
            # Passo 5: Combinar transcrição com diarização
            progress(0.9, desc="Combinando resultados...")
            combined_segments = self._combine_transcription_diarization(
                diarization_segments,
                transcription["segments"]
            )
            
            self.current_segments = combined_segments
            
            # Formata saída
            formatted = self._format_segments_for_display(combined_segments)
            mappings = self.speaker_mapper.get_all_mappings()
            
            progress(1.0, desc="Concluído!")
            
            return (
                f"✅ Processamento concluído!\n"
                f"• {len(diarization_segments)} segmentos detectados\n"
                f"• {len(set(s['speaker'] for s in diarization_segments))} falantes únicos\n"
                f"• {len(mappings)} falantes identificados por amostras",
                formatted,
                mappings
            )
            
        except Exception as e:
            return f"❌ Erro: {str(e)}", [], []
    
    def _combine_transcription_diarization(self, diarization: List[Dict],
                                          transcription: List[Dict]) -> List[Dict]:
        """
        Combina segmentos de diarização com transcrição
        
        Atribui texto transcrito aos segmentos de cada falante.
        """
        combined = []
        
        for diag_seg in diarization:
            diag_start = diag_seg["start"]
            diag_end = diag_seg["end"]
            
            # Encontra segmentos de transcrição que se sobrepõem
            overlapping_text = []
            for trans_seg in transcription:
                trans_start = trans_seg.get("start", 0)
                trans_end = trans_seg.get("end", 0)
                
                # Verifica sobreposição
                if trans_start <= diag_end and trans_end >= diag_start:
                    text = trans_seg.get("text", "").strip()
                    if text:
                        overlapping_text.append(text)
            
            combined.append({
                "speaker": diag_seg["speaker"],
                "start": diag_start,
                "end": diag_end,
                "text": " ".join(overlapping_text) if overlapping_text else "[sem áudio]",
                "identified_as": diag_seg.get("identified_as"),
                "confidence": diag_seg.get("confidence", 0.0)
            })
        
        return combined
    
    def _format_segments_for_display(self, segments: List[Dict]) -> List[List]:
        """Formata segmentos para tabela Gradio"""
        formatted = []
        
        for seg in sorted(segments, key=lambda x: x["start"]):
            speaker_id = seg.get("speaker", "UNKNOWN")
            speaker_name = self.speaker_mapper.get_name(speaker_id)
            
            start_fmt = self.formatter.format_timestamp(seg.get("start", 0))
            end_fmt = self.formatter.format_timestamp(seg.get("end", 0))
            
            formatted.append([
                start_fmt,
                end_fmt,
                speaker_id,
                speaker_name,
                seg.get("text", ""),
                f"{seg.get('confidence', 0):.2%}" if seg.get("identified_as") else "N/A"
            ])
        
        return formatted
    
    def update_speaker_mapping(self, speaker_id: str, name: str) -> str:
        """
        Atualiza mapeamento manual de falante
        
        Args:
            speaker_id: ID do falante (ex: SPEAKER_00)
            name: Nome real do falante
            
        Returns:
            Mensagem de confirmação
        """
        if not speaker_id or not name:
            return "⚠️ Preencha ambos os campos"
        
        self.speaker_mapper.map_speaker(speaker_id, name.strip(), method="manual")
        return f"✅ {speaker_id} mapeado como '{name.strip()}'"
    
    def generate_report(self, format_type: str = "markdown") -> str:
        """
        Gera relatório no formato especificado
        
        Args:
            format_type: Formato desejado ('markdown', 'txt', 'html')
            
        Returns:
            Caminho do arquivo gerado ou mensagem de erro
        """
        if not self.current_audio_path or not self.current_segments:
            return "❌ Processe um áudio primeiro"
        
        speaker_map = {m["speaker_id"]: m["name"] for m in self.speaker_mapper.get_all_mappings()}
        mappings = self.speaker_mapper.get_all_mappings()
        
        try:
            files = self.formatter.generate_full_report(
                self.current_audio_path,
                self.current_segments,
                speaker_map,
                mappings,
                formats=[format_type]
            )
            
            return f"✅ Relatório gerado: {files.get(format_type, 'desconhecido')}"
            
        except Exception as e:
            return f"❌ Erro ao gerar relatório: {str(e)}"
    
    def create_interface(self) -> gr.Blocks:
        """Cria interface Gradio completa"""
        
        with gr.Blocks(title="Transcritor Forense de Áudio") as app:
            gr.Markdown("""
            # 🎙️ Transcritor Forense de Áudio
            
            Ferramenta profissional para transcrição de áudio com validade jurídica.
            Utiliza **diarização acústica real** (pyannote.audio), **transcrição precisa** (whisperx) 
            e **identificação por amostras de voz** (speechbrain).
            """)
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📁 Entrada de Áudio")
                    audio_input = gr.File(label="Arquivo de Áudio", file_types=["audio"])
                    
                    gr.Markdown("### ⚙️ Parâmetros")
                    min_speakers = gr.Slider(1, 10, value=2, step=1, label="Mínimo de Falantes")
                    max_speakers = gr.Slider(1, 10, value=5, step=1, label="Máximo de Falantes")
                    
                    process_btn = gr.Button("🚀 Processar Áudio", variant="primary")
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🎤 Amostras de Referência (Opcional)")
                    gr.Markdown("Carregue amostras de voz para identificar falantes automaticamente")
                    
                    sample_inputs = []
                    default_names = ["Cliente", "Empresa", "Falante 3", "Falante 4", "Falante 5"]
                    
                    for i, name in enumerate(default_names):
                        with gr.Row():
                            sample_name = gr.Textbox(value=name, label="Nome", scale=1)
                            sample_file = gr.File(label="Amostra", file_types=["audio"], scale=2)
                            sample_inputs.append((sample_name, sample_file))
                    
                    load_samples_btn = gr.Button("Carregar Amostras")
                    sample_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("---")
            
            with gr.Row():
                with gr.Column(scale=2):
                    gr.Markdown("### 📝 Transcrição")
                    transcript_table = gr.Dataframe(
                        headers=["Início", "Fim", "ID Falante", "Nome", "Texto", "Confiança"],
                        label="Segmentos Transcritos",
                        wrap=True
                    )
                    
                    status_output = gr.Textbox(label="Status do Processamento", interactive=False)
                
                with gr.Column(scale=1):
                    gr.Markdown("### 🔧 Mapeamento Manual")
                    gr.Markdown("Corrija ou adicione nomes aos falantes detectados")
                    
                    with gr.Row():
                        speaker_id_input = gr.Textbox(label="ID do Falante", placeholder="SPEAKER_00")
                        speaker_name_input = gr.Textbox(label="Nome Real", placeholder="João Silva")
                    
                    map_btn = gr.Button("Atualizar Mapeamento")
                    map_status = gr.Textbox(label="Status Mapeamento", interactive=False)
                    
                    gr.Markdown("### 📄 Gerar Relatório")
                    report_format = gr.Radio(
                        choices=["markdown", "txt", "html"],
                        value="markdown",
                        label="Formato"
                    )
                    generate_btn = gr.Button("Gerar Relatório")
                    report_status = gr.Textbox(label="Relatório", interactive=False)
            
            # Event handlers
            load_samples_btn.click(
                fn=lambda *args: self.load_reference_samples(
                    [(name.value, file.value) for name, file in sample_inputs if name.value and file.value]
                ),
                inputs=[item for pair in sample_inputs for item in pair],
                outputs=sample_status
            )
            
            process_btn.click(
                fn=self.process_audio,
                inputs=[audio_input, min_speakers, max_speakers],
                outputs=[status_output, transcript_table, gr.State()]
            )
            
            map_btn.click(
                fn=self.update_speaker_mapping,
                inputs=[speaker_id_input, speaker_name_input],
                outputs=map_status
            )
            
            generate_btn.click(
                fn=self.generate_report,
                inputs=[report_format],
                outputs=report_status
            )
            
            gr.Markdown("""
            ---
            ### ℹ️ Informações Técnicas
            
            **Metodologia:**
            - **Diarização:** pyannote.audio 3.1 - Análise espectral acústica baseada em deep learning
            - **Transcrição:** whisperx 3.1 - Alinhamento fonético word-level com Whisper
            - **Identificação:** speechbrain 1.0 - Embeddings de voz ECAPA-TDNN
            
            **Validade Jurídica:**
            - Hash SHA-256 do áudio original incluso em todos os relatórios
            - Timestamps precisos com alinhamento fonético
            - Metadados completos de processamento
            - Documentação da metodologia aplicada
            """)
        
        return app
    
    def launch(self, server_name: str = "0.0.0.0", server_port: int = 7860,
               share: bool = False, **kwargs):
        """
        Lança a aplicação web
        
        Args:
            server_name: Endereço do servidor
            server_port: Porta do servidor
            share: Cria tunnel público (ngrok)
        """
        app = self.create_interface()
        app.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
            **kwargs
        )


def main():
    """Ponto de entrada principal"""
    app = ForensicTranscriberApp(config_path="config.yaml")
    app.launch()


if __name__ == "__main__":
    main()
