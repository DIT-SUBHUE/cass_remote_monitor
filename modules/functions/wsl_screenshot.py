"""
Função para capturar screenshot via WSL em diferentes cenários.
"""

import os
import platform
import subprocess
import tempfile
from datetime import datetime
from typing import Optional, Dict, List


def wsl_screenshot() -> Optional[str]:
    """
    Captura screenshot usando WSL, tentando diferentes métodos.
    
    Returns:
        Optional[str]: Caminho do arquivo da screenshot ou None se houver erro
    """
    try:
        # Verifica se está rodando no WSL
        if _is_running_in_wsl():
            return _wsl_screenshot_native()
        else:
            return _wsl_screenshot_from_windows()
    except Exception as e:
        print(f"Erro geral ao capturar screenshot WSL: {e}")
        return None


def _is_running_in_wsl() -> bool:
    """
    Verifica se o script está rodando dentro do WSL.
    
    Returns:
        bool: True se estiver no WSL
    """
    try:
        # Verifica se existe /proc/version com Microsoft
        if os.path.exists('/proc/version'):
            with open('/proc/version', 'r') as f:
                content = f.read().lower()
                return 'microsoft' in content or 'wsl' in content
        return False
    except:
        return False


def _wsl_screenshot_native() -> Optional[str]:
    """
    Captura screenshot de dentro do WSL usando ferramentas Linux.
    
    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = "/tmp"
    filepath = os.path.join(temp_dir, f"wsl_screenshot_{timestamp}.png")
    
    # Lista de métodos para tentar
    methods = [
        _try_scrot_screenshot,
        _try_gnome_screenshot,
        _try_imagemagick_screenshot,
        _try_x11_screenshot,
        _try_wayland_screenshot
    ]
    
    for method in methods:
        try:
            if method(filepath):
                return filepath
        except Exception as e:
            print(f"Método {method.__name__} falhou: {e}")
            continue
    
    return None


def _wsl_screenshot_from_windows() -> Optional[str]:
    """
    Captura screenshot chamando WSL de fora (do Windows).
    
    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, f"wsl_screenshot_{timestamp}.png")
    wsl_path = f"/tmp/wsl_screenshot_{timestamp}.png"
    
    # Comandos para tentar no WSL
    wsl_commands = [
        f'export DISPLAY=:0.0; scrot "{wsl_path}" 2>/dev/null',
        f'export DISPLAY=:0.0; gnome-screenshot -w -f "{wsl_path}" 2>/dev/null',
        f'export DISPLAY=:0.0; import -window root "{wsl_path}" 2>/dev/null',
        f'export WAYLAND_DISPLAY=wayland-0; grim "{wsl_path}" 2>/dev/null'
    ]
    
    for cmd in wsl_commands:
        try:
            # Executa comando no WSL
            result = subprocess.run(
                ['wsl', '-e', 'bash', '-c', cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Copia arquivo do WSL para Windows
                copy_result = subprocess.run(
                    ['wsl', '-e', 'cp', wsl_path, f'/mnt/c/temp/{os.path.basename(filepath)}'],
                    capture_output=True,
                    text=True
                )
                
                if copy_result.returncode == 0:
                    return f'C:/temp/{os.path.basename(filepath)}'
                    
        except Exception as e:
            print(f"Comando WSL falhou: {e}")
            continue
    
    return None


def _try_scrot_screenshot(filepath: str) -> bool:
    """Tenta capturar screenshot usando scrot."""
    try:
        # Tenta capturar tela inteira
        result = subprocess.run(
            ['scrot', filepath],
            capture_output=True,
            text=True,
            timeout=10,
            env=dict(os.environ, DISPLAY=':0.0')
        )
        return result.returncode == 0 and os.path.exists(filepath)
    except:
        return False


def _try_gnome_screenshot(filepath: str) -> bool:
    """Tenta capturar screenshot usando gnome-screenshot."""
    try:
        result = subprocess.run(
            ['gnome-screenshot', '-f', filepath],
            capture_output=True,
            text=True,
            timeout=10,
            env=dict(os.environ, DISPLAY=':0.0')
        )
        return result.returncode == 0 and os.path.exists(filepath)
    except:
        return False


def _try_imagemagick_screenshot(filepath: str) -> bool:
    """Tenta capturar screenshot usando ImageMagick."""
    try:
        result = subprocess.run(
            ['import', '-window', 'root', filepath],
            capture_output=True,
            text=True,
            timeout=10,
            env=dict(os.environ, DISPLAY=':0.0')
        )
        return result.returncode == 0 and os.path.exists(filepath)
    except:
        return False


def _try_x11_screenshot(filepath: str) -> bool:
    """Tenta capturar screenshot usando xwd."""
    try:
        # Captura usando xwd e converte para PNG
        result = subprocess.run(
            ['xwd', '-root', '-out', filepath + '.xwd'],
            capture_output=True,
            text=True,
            timeout=10,
            env=dict(os.environ, DISPLAY=':0.0')
        )
        
        if result.returncode == 0:
            # Converte XWD para PNG
            convert_result = subprocess.run(
                ['convert', filepath + '.xwd', filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Remove arquivo temporário
            try:
                os.remove(filepath + '.xwd')
            except:
                pass
                
            return convert_result.returncode == 0 and os.path.exists(filepath)
        return False
    except:
        return False


def _try_wayland_screenshot(filepath: str) -> bool:
    """Tenta capturar screenshot usando grim (Wayland)."""
    try:
        result = subprocess.run(
            ['grim', filepath],
            capture_output=True,
            text=True,
            timeout=10,
            env=dict(os.environ, WAYLAND_DISPLAY='wayland-0')
        )
        return result.returncode == 0 and os.path.exists(filepath)
    except:
        return False


def capture_zellij_sessions() -> Dict[str, any]:
    """
    Captura informações das sessões do Zellij.
    
    Returns:
        Dict: Informações das sessões e layouts
    """
    try:
        sessions_info = {}
        
        # Lista sessões ativas
        sessions_result = subprocess.run(
            ['zellij', 'list-sessions'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if sessions_result.returncode == 0:
            sessions_info['sessions'] = sessions_result.stdout
        
        # Tenta capturar layout da sessão ativa
        try:
            layout_result = subprocess.run(
                ['zellij', 'dump-layout'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if layout_result.returncode == 0:
                sessions_info['layout'] = layout_result.stdout
        except:
            pass
        
        return sessions_info
        
    except Exception as e:
        print(f"Erro ao capturar sessões Zellij: {e}")
        return {}


def get_wsl_screenshot_info() -> str:
    """
    Retorna informações sobre capacidades de screenshot no WSL.
    
    Returns:
        str: Informações sobre suporte a screenshot
    """
    info = []
    info.append("🐧 **WSL Screenshot Info:**")
    
    # Verifica se está no WSL
    if _is_running_in_wsl():
        info.append("✅ Executando dentro do WSL")
        
        # Verifica ferramentas disponíveis
        tools = [
            ('scrot', 'Screenshot tool'),
            ('gnome-screenshot', 'GNOME screenshot'),
            ('import', 'ImageMagick'),
            ('xwd', 'X11 window dump'),
            ('grim', 'Wayland screenshot'),
            ('zellij', 'Terminal multiplexer')
        ]
        
        info.append("🔧 **Ferramentas disponíveis:**")
        for tool, desc in tools:
            try:
                result = subprocess.run(
                    ['which', tool],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                status = "✅" if result.returncode == 0 else "❌"
                info.append(f"   {status} {tool} - {desc}")
            except:
                info.append(f"   ❌ {tool} - {desc}")
        
        # Verifica displays disponíveis
        displays = []
        for display in [':0.0', ':1.0', 'wayland-0']:
            env_var = 'DISPLAY' if display.startswith(':') else 'WAYLAND_DISPLAY'
            displays.append(f"   {display} ({env_var})")
        
        info.append("🖥️ **Displays testados:**")
        info.extend(displays)
        
    else:
        info.append("❌ Não executando no WSL")
        info.append("🔄 Tentará executar via 'wsl' command")
    
    return "\n".join(info)


def cleanup_wsl_screenshot(filepath: str) -> None:
    """
    Remove arquivo de screenshot temporário.
    
    Args:
        filepath: Caminho do arquivo a ser removido
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print(f"Screenshot WSL removida: {filepath}")
    except Exception as e:
        print(f"Erro ao remover screenshot WSL: {e}")


if __name__ == "__main__":
    # Teste da função
    print("=== TESTE WSL SCREENSHOT ===")
    print(get_wsl_screenshot_info())
    print("\n=== TESTANDO CAPTURA ===")
    
    screenshot_path = wsl_screenshot()
    if screenshot_path:
        print(f"✅ Screenshot capturada: {screenshot_path}")
        
        # Testa captura de sessões Zellij
        zellij_info = capture_zellij_sessions()
        if zellij_info:
            print("✅ Informações Zellij capturadas")
            print(f"Sessions: {len(zellij_info.get('sessions', '').splitlines())} linhas")
        
        # Limpa arquivo
        cleanup_wsl_screenshot(screenshot_path)
    else:
        print("❌ Falha ao capturar screenshot")
