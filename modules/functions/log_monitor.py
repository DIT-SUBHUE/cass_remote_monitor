"""
Função para monitorar logs de diferentes diretórios.
"""

import os
import glob
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


def get_tails(num_lines: int = 20) -> List[Dict[str, str]]:
    """
    Busca os últimos registros de log de todos os arquivos .log nos diretórios especificados.
    
    Args:
        num_lines: Número de linhas para fazer tail de cada arquivo (padrão: 20)
    
    Returns:
        List[Dict]: Lista com informações de cada arquivo de log encontrado
    """
    # Diretórios a serem monitorados (relativo ao diretório pai do start.py)
    target_dirs = [
        'centralizador_extract',
        'centralizador_transform', 
        'smsrio',
        'vitai'
    ]
    
    # Determina o diretório base (um nível acima do start.py)
    current_dir = Path(__file__).parent.parent.parent  # sai de functions/ -> modules/ -> cass_remote_monitor/
    base_dir = current_dir.parent  # sobe mais um nível
    
    log_results = []
    
    for dir_name in target_dirs:
        dir_path = base_dir / dir_name
        
        if not dir_path.exists():
            log_results.append({
                'directory': dir_name,
                'status': 'directory_not_found',
                'path': str(dir_path),
                'content': f"❌ Diretório não encontrado: {dir_path}",
                'file_count': 0
            })
            continue
        
        # Busca todos os arquivos .log na subpasta logs/
        logs_subdir = dir_path / 'logs'
        
        if not logs_subdir.exists():
            log_results.append({
                'directory': dir_name,
                'status': 'logs_subdir_not_found',
                'path': str(logs_subdir),
                'content': f"⚠️ Subpasta logs/ não encontrada em: {dir_path}",
                'file_count': 0
            })
            continue
        
        log_files = list(logs_subdir.glob('*.log'))
        
        if not log_files:
            log_results.append({
                'directory': dir_name,
                'status': 'no_logs_found',
                'path': str(logs_subdir),
                'content': f"⚠️ Nenhum arquivo .log encontrado em: {logs_subdir}",
                'file_count': 0
            })
            continue
        
        # Ordena arquivos por data de modificação (mais recente primeiro)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for log_file in log_files:
            try:
                content = _get_file_tail(log_file, num_lines)
                
                # Informações do arquivo
                stat = log_file.stat()
                modified_time = datetime.fromtimestamp(stat.st_mtime)
                file_size = stat.st_size
                
                log_results.append({
                    'directory': dir_name,
                    'status': 'success',
                    'file_name': log_file.name,
                    'file_path': str(log_file),
                    'file_size': file_size,
                    'modified_time': modified_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'content': content,
                    'line_count': len(content.splitlines()) if content else 0
                })
                
            except Exception as e:
                log_results.append({
                    'directory': dir_name,
                    'status': 'error',
                    'file_name': log_file.name,
                    'file_path': str(log_file),
                    'content': f"❌ Erro ao ler arquivo {log_file.name}: {str(e)}",
                    'error': str(e)
                })
    
    return log_results


def _get_file_tail(file_path: Path, num_lines: int) -> str:
    """
    Lê as últimas N linhas de um arquivo.
    
    Args:
        file_path: Caminho para o arquivo
        num_lines: Número de linhas para ler
        
    Returns:
        str: Conteúdo das últimas linhas
    """
    try:
        # Para arquivos pequenos, lê tudo
        if file_path.stat().st_size < 10000:  # 10KB
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                return ''.join(lines[-num_lines:])
        
        # Para arquivos grandes, usa método mais eficiente
        with open(file_path, 'rb') as f:
            # Move para o final do arquivo
            f.seek(0, 2)
            file_size = f.tell()
            
            # Estima posição inicial (aproximadamente)
            estimated_pos = max(0, file_size - (num_lines * 100))  # 100 chars por linha em média
            f.seek(estimated_pos)
            
            # Lê do ponto estimado até o final
            content = f.read().decode('utf-8', errors='ignore')
            lines = content.splitlines()
            
            # Retorna as últimas N linhas
            return '\n'.join(lines[-num_lines:])
            
    except Exception as e:
        return f"Erro ao ler arquivo: {str(e)}"


def format_log_message(log_info: Dict[str, str]) -> str:
    """
    Formata a informação de log para envio via Telegram.
    
    Args:
        log_info: Dicionário com informações do log
        
    Returns:
        str: Mensagem formatada
    """
    if log_info['status'] == 'directory_not_found':
        return f"📁 **{log_info['directory']}**\n{log_info['content']}"
    
    elif log_info['status'] == 'no_logs_found':
        return f"📁 **{log_info['directory']}**\n{log_info['content']}"
    
    elif log_info['status'] == 'error':
        return f"📁 **{log_info['directory']}** - {log_info['file_name']}\n{log_info['content']}"
    
    elif log_info['status'] == 'success':
        header = f"📁 **{log_info['directory']}** - `{log_info['file_name']}`\n"
        header += f"📅 Modificado: {log_info['modified_time']}\n"
        header += f"📊 Tamanho: {_format_file_size(log_info['file_size'])}\n"
        header += f"📄 Linhas mostradas: {log_info['line_count']}\n"
        header += "─" * 40 + "\n"
        
        # Limita o conteúdo para não exceder limite do Telegram
        content = log_info['content']
        if len(content) > 3500:  # Deixa espaço para o header
            content = content[-3500:] + "\n\n... (arquivo truncado)"
        
        return f"{header}```\n{content}\n```"
    
    return f"❓ Status desconhecido: {log_info.get('status', 'unknown')}"


def _format_file_size(size_bytes: int) -> str:
    """
    Formata tamanho do arquivo em formato legível.
    
    Args:
        size_bytes: Tamanho em bytes
        
    Returns:
        str: Tamanho formatado
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/(1024**2):.1f} MB"
    else:
        return f"{size_bytes/(1024**3):.1f} GB"


def get_logs_summary() -> str:
    """
    Retorna um resumo dos diretórios de log monitorados.
    
    Returns:
        str: Resumo formatado
    """
    target_dirs = ['centralizador_extract', 'centralizador_transform', 'smsrio', 'vitai']
    
    current_dir = Path(__file__).parent.parent.parent
    base_dir = current_dir.parent
    
    summary = "📋 **Resumo dos Diretórios de Log**\n\n"
    
    for dir_name in target_dirs:
        dir_path = base_dir / dir_name
        logs_subdir = dir_path / 'logs'
        
        if not dir_path.exists():
            summary += f"❌ `{dir_name}`: Diretório não encontrado\n"
            continue
            
        if not logs_subdir.exists():
            summary += f"⚠️ `{dir_name}`: Subpasta logs/ não encontrada\n"
            continue
        
        log_files = list(logs_subdir.glob('*.log'))
        
        if not log_files:
            summary += f"⚠️ `{dir_name}`: Sem arquivos .log na pasta logs/\n"
        else:
            # Arquivo mais recente
            latest_file = max(log_files, key=lambda x: x.stat().st_mtime)
            modified_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
            
            summary += f"✅ `{dir_name}`: {len(log_files)} arquivo(s)\n"
            summary += f"   📄 Mais recente: `{latest_file.name}`\n"
            summary += f"   📅 Modificado: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    return summary


def _escape_markdown(text: str) -> str:
    """
    Escapa caracteres especiais do Markdown para evitar erros de parsing no Telegram.
    
    Args:
        text: Texto a ser escapado
        
    Returns:
        str: Texto escapado
    """
    # Caracteres que podem causar problemas no Telegram Markdown
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text


def format_log_results_for_telegram(results: List[Dict[str, str]], max_message_length: int = 4000) -> List[str]:
    """
    Formata os resultados dos logs para envio via Telegram.
    Cada arquivo de log gera uma mensagem separada.
    
    Args:
        results: Lista de resultados dos logs
        max_message_length: Tamanho máximo de cada mensagem
        
    Returns:
        List[str]: Lista de mensagens formatadas para envio
    """
    messages = []
    
    for result in results:
        if result['status'] == 'success':
            # Mensagem para arquivo de log com conteúdo
            # Usa texto simples para evitar problemas de parsing
            message = f"📄 {result['directory']} - {result['file_name']}\n\n"
            message += f"📅 Modificado: {result['modified_time']}\n"
            message += f"📊 Tamanho: {_format_file_size(result['file_size'])}\n"
            message += f"📝 Linhas mostradas: {result['line_count']}\n\n"
            message += "───────────────────────────────\n"
            
            content = result['content']
            
            # Trunca o conteúdo se necessário
            available_space = max_message_length - len(message) - 20  # margem de segurança
            if len(content) > available_space:
                content = content[:available_space] + "\n... (truncado)"
            
            # Remove caracteres problemáticos do conteúdo
            content = content.replace('```', '---')  # Remove blocos de código
            content = content.replace('`', "'")       # Substitui backticks
            
            message += content
            
            messages.append(message)
            
        elif result['status'] in ['directory_not_found', 'logs_subdir_not_found', 'no_logs_found']:
            # Mensagem para diretórios sem logs
            message = f"⚠️ {result['directory']}\n\n"
            message += result['content']
            messages.append(message)
            
        elif result['status'] == 'error':
            # Mensagem para erros
            message = f"❌ {result['directory']}"
            if 'file_name' in result:
                message += f" - {result['file_name']}"
            message += "\n\n"
            message += result['content']
            messages.append(message)
    
    # Se não há mensagens, adiciona uma mensagem padrão
    if not messages:
        messages.append("⚠️ Nenhum log encontrado nos diretórios monitorados.")
    
    return messages


if __name__ == "__main__":
    # Teste das funções
    print("=== TESTE LOG MONITOR ===")
    print(get_logs_summary())
    print("\n=== BUSCANDO LOGS ===")
    
    logs = get_tails(10)
    for log_info in logs:
        print(f"\n{format_log_message(log_info)}")
        print("=" * 50)
    
    print("\n=== FORMATANDO PARA TELEGRAM ===")
    telegram_messages = format_log_results_for_telegram(logs)
    for msg in telegram_messages:
        print(msg)
        print("=" * 50)
