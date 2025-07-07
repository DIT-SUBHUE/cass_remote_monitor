#!/usr/bin/env python3
"""
Monitor de mensagens do Telegram
Monitora o chat, loga mensagens e responde ao comando /ping
"""

import asyncio
import os

from dotenv import load_dotenv

from modules.telegram_monitor import TelegramMonitor

load_dotenv()


async def main():
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    if not TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID devem estar no .env")
        return

    print("🤖 Iniciando Monitor do Telegram...")
    print(f"📱 Chat ID: {CHAT_ID}")
    print()
    print("✅ Comandos disponíveis:")
    print("   • /ping - Responde com 'Pong! 🏓'")
    print("   • /status - Mostra informações do sistema")
    print("   • /screenshot - Captura screenshot da tela")
    print("   • /wsl_screenshot - Captura screenshot via WSL")
    print()
    print("⏹️  Para parar o monitor, pressione Ctrl+C")
    print("=" * 50)

    monitor = TelegramMonitor(TOKEN, CHAT_ID)

    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\nMonitor parado")


if __name__ == "__main__":
    asyncio.run(main())
