"""
Função para capturar screenshot da tela.
"""

import os
import platform
import tempfile
from datetime import datetime
from typing import Optional


def take_screenshot() -> Optional[str]:
    """
    Captura uma screenshot da tela e salva em arquivo temporário.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot ou None se houver erro
    """
    try:
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
        import pyscreenshot as ImageGrab

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
        print("pyscreenshot não está instalado. Tentando método alternativo...")
        return _take_screenshot_alternative()
    except Exception as e:
        print(f"Erro ao capturar screenshot no Linux: {e}")
        return None


def _take_screenshot_macos() -> Optional[str]:
    """
    Captura screenshot no macOS usando screencapture.

    Returns:
        Optional[str]: Caminho do arquivo da screenshot
    """
    try:
        import subprocess

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

    # Verifica dependências
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
