"""
Função para capturar screenshot da tela.
"""

import os
import platform
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional


def take_screenshot() -> Optional[str]:
    """
    Captura uma screenshot da tela e salva em arquivo temporário.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot ou None se houver erro
    """
    try:
        # Verifica se está rodando no WSL primeiro
        if _is_running_in_wsl():
            print("Detectado WSL - usando método PowerShell")
            return _take_screenshot_wsl_powershell()
        
        # Importa a biblioteca apropriada baseada no sistema operacional
        system = platform.system().lower()

        if system == "windows":
            return _take_screenshot_windows()
        elif system == "linux":
            return _take_screenshot_linux()
        elif system == "darwin":  # macOS
            return _take_screenshot_macos()
        else:
            print(f"Sistema operacional não suportado: {system}")
            return None

    except Exception as e:
        print(f"Erro ao capturar screenshot: {e}")
        return None


def _take_screenshot_windows() -> Optional[str]:
    """
    Captura screenshot no Windows usando PIL/Pillow.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    try:
        from PIL import ImageGrab

        # Captura a screenshot
        screenshot = ImageGrab.grab()

        # Cria arquivo temporário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, f"screenshot_{timestamp}.png")

        # Salva a screenshot
        screenshot.save(filepath, "PNG")

        return filepath

    except ImportError:
        print("PIL/Pillow não está instalado. Tentando método alternativo...")
        return _take_screenshot_alternative()
    except Exception as e:
        print(f"Erro ao capturar screenshot no Windows: {e}")
        return None


def _take_screenshot_linux() -> Optional[str]:
    """
    Captura screenshot no Linux usando pyscreenshot.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    try:
        # Verifica se há um display disponível
        if not os.environ.get('DISPLAY') and not os.environ.get('WAYLAND_DISPLAY'):
            print("Nenhum display gráfico disponível (DISPLAY ou WAYLAND_DISPLAY)")
            return _take_screenshot_alternative()
        
        import pyscreenshot as ImageGrab

        # Captura a screenshot com timeout
        screenshot = ImageGrab.grab()

        # Cria arquivo temporário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, f"screenshot_{timestamp}.png")

        # Salva a screenshot
        screenshot.save(filepath, "PNG")

        return filepath

    except ImportError:
        print("pyscreenshot não está instalado. Tentando método alternativo...")
        return _take_screenshot_alternative()
    except Exception as e:
        print(f"Erro ao capturar screenshot no Linux: {e}")
        return _take_screenshot_alternative()


def _take_screenshot_macos() -> Optional[str]:
    """
    Captura screenshot no macOS usando screencapture.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    try:
        # Cria arquivo temporário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, f"screenshot_{timestamp}.png")

        # Usa o comando screencapture do macOS
        result = subprocess.run(
            ["screencapture", "-x", filepath], capture_output=True, text=True
        )

        if result.returncode == 0 and os.path.exists(filepath):
            return filepath
        else:
            print(f"Erro ao executar screencapture: {result.stderr}")
            return None

    except Exception as e:
        print(f"Erro ao capturar screenshot no macOS: {e}")
        return None


def _take_screenshot_alternative() -> Optional[str]:
    """
    Método alternativo usando PIL/Pillow para qualquer sistema.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    try:
        from PIL import ImageGrab

        # Captura a screenshot
        screenshot = ImageGrab.grab()

        # Cria arquivo temporário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, f"screenshot_{timestamp}.png")

        # Salva a screenshot
        screenshot.save(filepath, "PNG")

        return filepath

    except Exception as e:
        print(f"Erro no método alternativo: {e}")
        return None


def cleanup_screenshot(filepath: str) -> None:
    """
    Remove o arquivo de screenshot temporário.

    Args:
        filepath: Caminho do arquivo a ser removido
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            print(f"Screenshot temporária removida: {filepath}")
    except Exception as e:
        print(f"Erro ao remover screenshot temporária: {e}")


def get_screenshot_info() -> str:
    """
    Retorna informações sobre a capacidade de screenshot do sistema.

    Returns:
        str: Informações sobre suporte a screenshot
    """
    system = platform.system().lower()

    info = f"🖼️ **Informações de Screenshot:**\n"
    info += f"💻 Sistema: {platform.system()}\n"
    
    # Verifica se está no WSL
    if _is_running_in_wsl():
        info += "🐧 Ambiente: WSL (Windows Subsystem for Linux)\n"
        info += "🔧 Método: PowerShell via WSL\n"
        
        # Testa se PowerShell está disponível
        try:
            result = subprocess.run(
                ['powershell.exe', '-Command', 'Get-Command Add-Type'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                info += "✅ PowerShell: Disponível\n"
            else:
                info += "❌ PowerShell: Não disponível\n"
        except:
            info += "❌ PowerShell: Erro ao verificar\n"
            
        return info

    # Verifica dependências para outros sistemas
    dependencies = []

    try:
        import PIL
        dependencies.append("✅ PIL/Pillow")
    except ImportError:
        dependencies.append("❌ PIL/Pillow (não instalado)")

    try:
        import pyscreenshot
        dependencies.append("✅ pyscreenshot")
    except ImportError:
        dependencies.append("❌ pyscreenshot (não instalado)")

    info += "📦 Dependências:\n"
    for dep in dependencies:
        info += f"   {dep}\n"

    # Informações específicas do sistema
    if system == "windows":
        info += "🔧 Método: ImageGrab (PIL/Pillow)\n"
    elif system == "linux":
        info += "🔧 Método: pyscreenshot + backends disponíveis\n"
    elif system == "darwin":
        info += "🔧 Método: screencapture (nativo macOS)\n"

    return info


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


def _take_screenshot_wsl_powershell() -> Optional[str]:
    """
    Captura screenshot usando PowerShell do Windows via WSL.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    try:
        # Cria nome do arquivo temporário
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_dir = "/tmp"
        wsl_filepath = os.path.join(temp_dir, f"screenshot_{timestamp}.png")
        
        # Converte caminho WSL para Windows
        wslpath_result = subprocess.run(
            ['wslpath', '-w', wsl_filepath],
            capture_output=True,
            text=True
        )
        
        if wslpath_result.returncode != 0:
            print("Erro ao converter caminho WSL para Windows")
            return None
            
        windows_path = wslpath_result.stdout.strip()
        
        # Script PowerShell para capturar screenshot
        powershell_script = f'''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$bitmap = New-Object System.Drawing.Bitmap $screen.Bounds.Width, $screen.Bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($screen.Bounds.X, $screen.Bounds.Y, 0, 0, $screen.Bounds.Size)

$bitmap.Save('{windows_path}', [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()

Write-Output "Screenshot saved successfully"
'''

        # Executa o script PowerShell
        result = subprocess.run(
            ['powershell.exe', '-Command', powershell_script],
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0 and os.path.exists(wsl_filepath):
            print(f"Screenshot capturada via PowerShell: {wsl_filepath}")
            return wsl_filepath
        else:
            print(f"Erro PowerShell (código {result.returncode}): {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Timeout ao executar PowerShell")
        return None
    except Exception as e:
        print(f"Erro ao capturar screenshot via PowerShell: {e}")
        return None


if __name__ == "__main__":
    # Teste da função
    print("Testando captura de screenshot...")
    print(get_screenshot_info())

    filepath = take_screenshot()
    if filepath:
        print(f"Screenshot capturada: {filepath}")
        print("Removendo arquivo temporário...")
        cleanup_screenshot(filepath)
    else:
        print("Falha ao capturar screenshot")
