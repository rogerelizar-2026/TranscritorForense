"""
Módulo de Formatação Forense
Gera documentos em MD/TXT/HTML com formatação jurídica
"""

import hashlib
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from jinja2 import Environment, FileSystemLoader, BaseLoader


class ForensicFormatter:
    """
    Gerador de relatórios forenses com validade jurídica
    
    Produz documentos em múltiplos formatos (Markdown, TXT, HTML)
    com metadados técnicos e hashes criptográficos para verificação.
    """
    
    def __init__(self, output_dir: str = "output", templates_dir: str = "templates"):
        """
        Inicializa o formatador forense
        
        Args:
            output_dir: Diretório para salvar relatórios gerados
            templates_dir: Diretório com templates Jinja2
        """
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Configura Jinja2
        if os.path.exists(templates_dir):
            self.env = Environment(loader=FileSystemLoader(templates_dir))
        else:
            # Usa templates embutidos se diretório não existir
            self.env = Environment(loader=BaseLoader())
            
    def compute_file_hash(self, file_path: str, algorithm: str = "sha256") -> str:
        """
        Calcula hash criptográfico do arquivo
        
        Args:
            file_path: Caminho para o arquivo
            algorithm: Algoritmo de hash ('sha256', 'sha512', 'md5')
            
        Returns:
            Hash hexadecimal do arquivo
        """
        hash_func = getattr(hashlib, algorithm)()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
                
        return hash_func.hexdigest()
    
    def compute_content_hash(self, content: str, algorithm: str = "sha256") -> str:
        """
        Calcula hash criptográfico do conteúdo
        
        Args:
            content: Conteúdo em string
            algorithm: Algoritmo de hash
            
        Returns:
            Hash hexadecimal do conteúdo
        """
        hash_func = getattr(hashlib, algorithm)()
        hash_func.update(content.encode('utf-8'))
        return hash_func.hexdigest()
    
    def format_timestamp(self, seconds: float) -> str:
        """
        Formata segundos em timestamp legível
        
        Args:
            seconds: Tempo em segundos
            
        Returns:
            String formatada como HH:MM:SS.mmm
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        millis = int((secs % 1) * 1000)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{int(secs):02d}.{millis:03d}"
        else:
            return f"{minutes:02d}:{int(secs):02d}.{millis:03d}"
    
    def generate_metadata(self, audio_path: str, segments: List[Dict[str, Any]],
                         speaker_mappings: List[Dict]) -> Dict[str, Any]:
        """
        Gera metadados forenses do documento
        
        Args:
            audio_path: Caminho para o arquivo de áudio original
            segments: Segmentos transcritos com diarização
            speaker_mappings: Mapeamentos de falantes
            
        Returns:
            Dicionário com metadados forenses
        """
        return {
            "audio_file": os.path.basename(audio_path),
            "audio_path": os.path.abspath(audio_path),
            "audio_hash_sha256": self.compute_file_hash(audio_path),
            "processing_date": datetime.now().isoformat(),
            "total_segments": len(segments),
            "total_duration": max(seg.get("end", 0) for seg in segments) if segments else 0,
            "speakers_identified": len(set(seg.get("speaker", "") for seg in segments)),
            "speaker_mappings": speaker_mappings,
            "tool_version": "1.0.0",
            "methodology": {
                "diarization": "pyannote.audio - análise espectral acústica",
                "transcription": "whisperx - alinhamento fonético",
                "speaker_identification": "speechbrain - embeddings de voz"
            }
        }
    
    def format_markdown(self, segments: List[Dict[str, Any]], 
                       metadata: Dict[str, Any],
                       speaker_map: Dict[str, str]) -> str:
        """
        Gera relatório em formato Markdown
        
        Args:
            segments: Segmentos transcritos
            metadata: Metadados forenses
            speaker_map: Mapeamento de IDs para nomes
            
        Returns:
            String formatada em Markdown
        """
        lines = []
        
        # Cabeçalho forense
        lines.append("# RELATÓRIO DE TRANSCRIÇÃO FORENSE")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Metadados
        lines.append("## METADADOS TÉCNICOS")
        lines.append("")
        lines.append(f"- **Arquivo de Áudio:** {metadata['audio_file']}")
        lines.append(f"- **Caminho Completo:** {metadata['audio_path']}")
        lines.append(f"- **Hash SHA-256:** `{metadata['audio_hash_sha256']}`")
        lines.append(f"- **Data de Processamento:** {metadata['processing_date']}")
        lines.append(f"- **Duração Total:** {self.format_timestamp(metadata['total_duration'])}")
        lines.append(f"- **Total de Segmentos:** {metadata['total_segments']}")
        lines.append(f"- **Falantes Identificados:** {metadata['speakers_identified']}")
        lines.append("")
        
        # Mapeamento de falantes
        if speaker_map:
            lines.append("## MAPEAMENTO DE FALANTES")
            lines.append("")
            lines.append("| ID Original | Nome Identificado | Método | Confiança |")
            lines.append("|-------------|-------------------|--------|-----------|")
            for mapping in metadata.get("speaker_mappings", []):
                speaker_id = mapping.get("speaker_id", "")
                name = mapping.get("name", "")
                method = mapping.get("method", "N/A")
                confidence = f"{mapping.get('confidence', 0):.2%}"
                lines.append(f"| {speaker_id} | {name} | {method} | {confidence} |")
            lines.append("")
        
        # Transcrição
        lines.append("## TRANSCRIÇÃO")
        lines.append("")
        
        current_speaker = None
        for segment in segments:
            speaker_id = segment.get("speaker", "UNKNOWN")
            speaker_name = speaker_map.get(speaker_id, speaker_id)
            start = self.format_timestamp(segment.get("start", 0))
            end = self.format_timestamp(segment.get("end", 0))
            text = segment.get("text", "[inaudível]")
            
            if speaker_name != current_speaker:
                lines.append(f"**[{start}] {speaker_name}:**")
                current_speaker = speaker_name
            
            lines.append(f"  {text}")
            lines.append("")
        
        # Rodapé técnico
        lines.append("---")
        lines.append("")
        lines.append("## VALIDAÇÃO TÉCNICA")
        lines.append("")
        lines.append("Este documento foi gerado automaticamente pelo Transcritor Forense de Áudio v1.0.0")
        lines.append("")
        lines.append("### Metodologia")
        lines.append("")
        lines.append(f"- **Diarização:** {metadata['methodology']['diarization']}")
        lines.append(f"- **Transcrição:** {metadata['methodology']['transcription']}")
        lines.append(f"- **Identificação:** {metadata['methodology']['speaker_identification']}")
        lines.append("")
        lines.append("### Hash de Verificação do Conteúdo")
        lines.append("")
        content = "\n".join(lines)
        content_hash = self.compute_content_hash(content)
        lines.append(f"`{content_hash}`")
        lines.append("")
        
        return "\n".join(lines)
    
    def format_txt(self, segments: List[Dict[str, Any]],
                  metadata: Dict[str, Any],
                  speaker_map: Dict[str, str]) -> str:
        """
        Gera relatório em formato TXT simples
        
        Args:
            segments: Segmentos transcritos
            metadata: Metadados forenses
            speaker_map: Mapeamento de IDs para nomes
            
        Returns:
            String formatada em texto puro
        """
        lines = []
        
        lines.append("=" * 70)
        lines.append("RELATÓRIO DE TRANSCRIÇÃO FORENSE")
        lines.append("=" * 70)
        lines.append("")
        lines.append(f"Arquivo: {metadata['audio_file']}")
        lines.append(f"Hash SHA-256: {metadata['audio_hash_sha256']}")
        lines.append(f"Processamento: {metadata['processing_date']}")
        lines.append(f"Duração: {self.format_timestamp(metadata['total_duration'])}")
        lines.append("")
        lines.append("-" * 70)
        lines.append("TRANSCRIÇÃO")
        lines.append("-" * 70)
        lines.append("")
        
        for segment in segments:
            speaker_id = segment.get("speaker", "UNKNOWN")
            speaker_name = speaker_map.get(speaker_id, speaker_id)
            start = self.format_timestamp(segment.get("start", 0))
            text = segment.get("text", "[inaudível]")
            
            lines.append(f"[{start}] {speaker_name}: {text}")
        
        lines.append("")
        lines.append("=" * 70)
        lines.append(f"Gerado por Transcritor Forense v1.0.0")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def format_html(self, segments: List[Dict[str, Any]],
                   metadata: Dict[str, Any],
                   speaker_map: Dict[str, str]) -> str:
        """
        Gera relatório em formato HTML
        
        Args:
            segments: Segmentos transcritos
            metadata: Metadados forenses
            speaker_map: Mapeamento de IDs para nomes
            
        Returns:
            String formatada em HTML
        """
        template_str = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Forense - {{ metadata.audio_file }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
        .metadata { background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }
        .transcript { margin: 20px 0; }
        .segment { margin: 10px 0; padding: 10px; border-left: 3px solid #3498db; }
        .speaker { font-weight: bold; color: #2c3e50; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #bdc3c7; font-size: 0.9em; color: #7f8c8d; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background: #3498db; color: white; }
        .hash { font-family: monospace; background: #f4f4f4; padding: 2px 5px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>RELATÓRIO DE TRANSCRIÇÃO FORENSE</h1>
    </div>
    
    <div class="metadata">
        <h2>METADADOS TÉCNICOS</h2>
        <p><strong>Arquivo:</strong> {{ metadata.audio_file }}</p>
        <p><strong>Caminho:</strong> {{ metadata.audio_path }}</p>
        <p><strong>Hash SHA-256:</strong> <span class="hash">{{ metadata.audio_hash_sha256 }}</span></p>
        <p><strong>Processamento:</strong> {{ metadata.processing_date }}</p>
        <p><strong>Duração:</strong> {{ metadata.total_duration_formatted }}</p>
        <p><strong>Segmentos:</strong> {{ metadata.total_segments }}</p>
        <p><strong>Falantes:</strong> {{ metadata.speakers_identified }}</p>
        
        {% if speaker_mappings %}
        <h3>Mapeamento de Falantes</h3>
        <table>
            <tr><th>ID Original</th><th>Nome</th><th>Método</th><th>Confiança</th></tr>
            {% for mapping in speaker_mappings %}
            <tr>
                <td>{{ mapping.speaker_id }}</td>
                <td>{{ mapping.name }}</td>
                <td>{{ mapping.method }}</td>
                <td>{{ "%.2f"|format(mapping.confidence * 100) }}%</td>
            </tr>
            {% endfor %}
        </table>
        {% endif %}
    </div>
    
    <div class="transcript">
        <h2>TRANSCRIÇÃO</h2>
        {% for segment in segments %}
        <div class="segment">
            <span class="timestamp">[{{ segment.timestamp_start }}]</span>
            <span class="speaker">{{ segment.speaker_name }}:</span>
            <span class="text">{{ segment.text }}</span>
        </div>
        {% endfor %}
    </div>
    
    <div class="footer">
        <h3>VALIDAÇÃO TÉCNICA</h3>
        <p>Este documento foi gerado automaticamente pelo <strong>Transcritor Forense de Áudio v1.0.0</strong></p>
        <p><strong>Metodologia:</strong></p>
        <ul>
            <li>Diarização: pyannote.audio - análise espectral acústica</li>
            <li>Transcrição: whisperx - alinhamento fonético</li>
            <li>Identificação: speechbrain - embeddings de voz</li>
        </ul>
        <p><strong>Hash do Conteúdo:</strong> <span class="hash">{{ content_hash }}</span></p>
    </div>
</body>
</html>"""
        
        template = self.env.from_string(template_str)
        
        # Prepara dados para template
        formatted_segments = []
        for segment in segments:
            speaker_id = segment.get("speaker", "UNKNOWN")
            formatted_segments.append({
                "timestamp_start": self.format_timestamp(segment.get("start", 0)),
                "timestamp_end": self.format_timestamp(segment.get("end", 0)),
                "speaker_name": speaker_map.get(speaker_id, speaker_id),
                "text": segment.get("text", "[inaudível]")
            })
        
        metadata["total_duration_formatted"] = self.format_timestamp(metadata.get("total_duration", 0))
        
        html_content = template.render(
            segments=formatted_segments,
            metadata=metadata,
            speaker_mappings=metadata.get("speaker_mappings", []),
            content_hash=self.compute_content_hash("")  # Será calculado após renderização
        )
        
        # Recalcula hash do conteúdo final
        content_hash = self.compute_content_hash(html_content)
        html_content = template.render(
            segments=formatted_segments,
            metadata=metadata,
            speaker_mappings=metadata.get("speaker_mappings", []),
            content_hash=content_hash
        )
        
        return html_content
    
    def save_report(self, content: str, filename: str, format_type: str) -> str:
        """
        Salva relatório em arquivo
        
        Args:
            content: Conteúdo do relatório
            filename: Nome base do arquivo (sem extensão)
            format_type: Tipo de formato ('markdown', 'txt', 'html')
            
        Returns:
            Caminho completo do arquivo salvo
        """
        extensions = {
            "markdown": ".md",
            "txt": ".txt",
            "html": ".html"
        }
        
        ext = extensions.get(format_type, ".txt")
        filepath = os.path.join(self.output_dir, f"{filename}{ext}")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        return filepath
    
    def generate_full_report(self, audio_path: str, segments: List[Dict[str, Any]],
                            speaker_map: Dict[str, str],
                            speaker_mappings: List[Dict],
                            formats: List[str] = ["markdown", "txt", "html"],
                            filename_prefix: Optional[str] = None) -> Dict[str, str]:
        """
        Gera relatório completo em múltiplos formatos
        
        Args:
            audio_path: Caminho para arquivo de áudio
            segments: Segmentos transcritos com diarização
            speaker_map: Mapeamento de IDs para nomes
            speaker_mappings: Lista de mapeamentos com metadados
            formats: Lista de formatos para gerar
            filename_prefix: Prefixo para nome do arquivo
            
        Returns:
            Dicionário com caminhos dos arquivos gerados
        """
        # Gera metadados
        metadata = self.generate_metadata(audio_path, segments, speaker_mappings)
        
        # Gera nome base do arquivo
        if filename_prefix is None:
            filename_prefix = f"forense_{os.path.splitext(os.path.basename(audio_path))[0]}"
        
        generated_files = {}
        
        for fmt in formats:
            if fmt == "markdown":
                content = self.format_markdown(segments, metadata, speaker_map)
            elif fmt == "txt":
                content = self.format_txt(segments, metadata, speaker_map)
            elif fmt == "html":
                content = self.format_html(segments, metadata, speaker_map)
            else:
                continue
                
            filepath = self.save_report(content, filename_prefix, fmt)
            generated_files[fmt] = filepath
            
        return generated_files
