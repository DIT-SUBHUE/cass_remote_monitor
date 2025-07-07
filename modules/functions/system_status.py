"""
Função para obter informações de status do sistema.
"""

import getpass
import os
import platform
import socket
from typing import Any, Dict, List

import psutil


def get_network_interfaces() -> List[Dict[str, Any]]:
    """
    Obtém informações das interfaces de rede conectadas.

    Returns:
        List[Dict]: Lista com informações das interfaces de rede
    """
    interfaces = []

    try:
        # Obtém estatísticas das interfaces de rede
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()

        for interface_name, interface_addresses in net_if_addrs.items():
            # Pula interfaces loopback e desconectadas
            if interface_name.startswith("lo") or interface_name.startswith("Local"):
                continue

            # Verifica se a interface está ativa
            if interface_name in net_if_stats:
                stats = net_if_stats[interface_name]
                if not stats.isup:
                    continue

            # Extrai informações da interface
            interface_info = {
                "name": interface_name,
                "type": "Unknown",
                "addresses": [],
            }

            # Determina o tipo da interface
            if (
                "wifi" in interface_name.lower()
                or "wlan" in interface_name.lower()
                or "wireless" in interface_name.lower()
            ):
                interface_info["type"] = "WiFi"
            elif (
                "eth" in interface_name.lower()
                or "ethernet" in interface_name.lower()
                or "local" in interface_name.lower()
            ):
                interface_info["type"] = "Ethernet"
            elif "ppp" in interface_name.lower() or "mobile" in interface_name.lower():
                interface_info["type"] = "Mobile"

            # Adiciona endereços IP
            for addr in interface_addresses:
                if addr.family == socket.AF_INET:  # IPv4
                    interface_info["addresses"].append(
                        {"ip": addr.address, "netmask": addr.netmask, "type": "IPv4"}
                    )
                elif addr.family == socket.AF_INET6:  # IPv6
                    interface_info["addresses"].append(
                        {"ip": addr.address, "netmask": addr.netmask, "type": "IPv6"}
                    )

            # Só adiciona se tiver endereços válidos
            if interface_info["addresses"]:
                interfaces.append(interface_info)

    except Exception as e:
        print(f"Erro ao obter interfaces de rede: {e}")

    return interfaces


def get_disk_usage() -> Dict[str, Any]:
    """
    Obtém informações de uso do disco.

    Returns:
        Dict: Informações de uso do disco
    """
    disk_info = {}

    try:
        # Obtém uso do disco da partição raiz
        if platform.system() == "Windows":
            disk_usage = psutil.disk_usage("C:\\")
        else:
            disk_usage = psutil.disk_usage("/")

        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        percent_used = (used_gb / total_gb) * 100

        disk_info = {
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "percent_used": round(percent_used, 2),
        }

    except Exception as e:
        print(f"Erro ao obter informações do disco: {e}")
        disk_info = {
            "total_gb": "N/A",
            "used_gb": "N/A",
            "free_gb": "N/A",
            "percent_used": "N/A",
        }

    return disk_info


def get_memory_info() -> Dict[str, Any]:
    """
    Obtém informações de memória RAM.

    Returns:
        Dict: Informações de memória
    """
    memory_info = {}

    try:
        memory = psutil.virtual_memory()
        total_gb = memory.total / (1024**3)
        used_gb = memory.used / (1024**3)
        available_gb = memory.available / (1024**3)

        memory_info = {
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "available_gb": round(available_gb, 2),
            "percent_used": round(memory.percent, 2),
        }

    except Exception as e:
        print(f"Erro ao obter informações da memória: {e}")
        memory_info = {
            "total_gb": "N/A",
            "used_gb": "N/A",
            "available_gb": "N/A",
            "percent_used": "N/A",
        }

    return memory_info


def get_cpu_info() -> Dict[str, Any]:
    """
    Obtém informações do processador.

    Returns:
        Dict: Informações do CPU
    """
    cpu_info = {}

    try:
        # Informações básicas do CPU
        cpu_info["cores_physical"] = psutil.cpu_count(logical=False)
        cpu_info["cores_logical"] = psutil.cpu_count(logical=True)
        cpu_info["usage_percent"] = round(psutil.cpu_percent(interval=1), 2)

        # Frequência do CPU
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            cpu_info["frequency_current"] = round(cpu_freq.current, 2)
            cpu_info["frequency_max"] = round(cpu_freq.max, 2)
        else:
            cpu_info["frequency_current"] = "N/A"
            cpu_info["frequency_max"] = "N/A"

    except Exception as e:
        print(f"Erro ao obter informações do CPU: {e}")
        cpu_info = {
            "cores_physical": "N/A",
            "cores_logical": "N/A",
            "usage_percent": "N/A",
            "frequency_current": "N/A",
            "frequency_max": "N/A",
        }

    return cpu_info


def get_system_info() -> Dict[str, Any]:
    """
    Obtém informações gerais do sistema.

    Returns:
        Dict: Informações do sistema
    """
    system_info = {}

    try:
        system_info["username"] = getpass.getuser()
    except Exception:
        system_info["username"] = "N/A"

    try:
        system_info["hostname"] = socket.gethostname()
    except Exception:
        system_info["hostname"] = "N/A"

    try:
        system_info["os"] = f"{platform.system()} {platform.release()}"
    except Exception:
        system_info["os"] = "N/A"

    try:
        system_info["architecture"] = platform.machine()
    except Exception:
        system_info["architecture"] = "N/A"

    try:
        system_info["processor"] = platform.processor()
    except Exception:
        system_info["processor"] = "N/A"

    try:
        boot_time = psutil.boot_time()
        from datetime import datetime

        boot_time_str = datetime.fromtimestamp(boot_time).strftime("%Y-%m-%d %H:%M:%S")
        system_info["boot_time"] = boot_time_str
    except Exception:
        system_info["boot_time"] = "N/A"

    return system_info


def system_status() -> str:
    """
    Gera um relatório completo de status do sistema.

    Returns:
        str: Relatório formatado com informações do sistema
    """
    # Obtém todas as informações
    system_info = get_system_info()
    cpu_info = get_cpu_info()
    memory_info = get_memory_info()
    disk_info = get_disk_usage()
    network_interfaces = get_network_interfaces()

    # Constrói o relatório
    report = []
    report.append("🖥️ **STATUS DO SISTEMA**")
    report.append("=" * 30)
    report.append("")

    # Informações gerais
    report.append("📋 **Informações Gerais:**")
    report.append(f"👤 Nome de usuário: {system_info['username']}")
    report.append(f"🏠 Hostname: {system_info['hostname']}")
    report.append(f"💻 Sistema Operacional: {system_info['os']}")
    report.append(f"🏗️ Arquitetura: {system_info['architecture']}")
    report.append(f"🔧 Processador: {system_info['processor']}")
    report.append(f"🔄 Último boot: {system_info['boot_time']}")
    report.append("")

    # Informações do CPU
    report.append("⚡ **Processador:**")
    report.append(f"🔢 Núcleos físicos: {cpu_info['cores_physical']}")
    report.append(f"🔢 Núcleos lógicos: {cpu_info['cores_logical']}")
    report.append(f"📊 Uso atual: {cpu_info['usage_percent']}%")
    report.append(f"📈 Frequência atual: {cpu_info['frequency_current']} MHz")
    report.append(f"📈 Frequência máxima: {cpu_info['frequency_max']} MHz")
    report.append("")

    # Informações de memória
    report.append("🧠 **Memória RAM:**")
    report.append(f"💾 Total: {memory_info['total_gb']} GB")
    report.append(
        f"📊 Usado: {memory_info['used_gb']} GB ({memory_info['percent_used']}%)"
    )
    report.append(f"🆓 Disponível: {memory_info['available_gb']} GB")
    report.append("")

    # Informações de armazenamento
    report.append("💿 **Armazenamento:**")
    report.append(f"💾 Total: {disk_info['total_gb']} GB")
    report.append(f"📊 Usado: {disk_info['used_gb']} GB ({disk_info['percent_used']}%)")
    report.append(f"🆓 Livre: {disk_info['free_gb']} GB")
    report.append("")

    # Informações de rede
    report.append("🌐 **Redes Conectadas:**")
    if network_interfaces:
        for interface in network_interfaces:
            report.append(f"📶 **{interface['type']}** ({interface['name']}):")
            for addr in interface["addresses"]:
                report.append(f"   📍 {addr['type']}: {addr['ip']}")
            report.append("")
    else:
        report.append("❌ Nenhuma interface de rede ativa encontrada")
        report.append("")

    return "\n".join(report)


if __name__ == "__main__":
    # Teste da função
    print(system_status())
