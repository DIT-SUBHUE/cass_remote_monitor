import asyncio
import logging
import os
from typing import Any, Callable, Dict

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Importa as funções
from .functions.ping import ping_response
from .functions.screenshot import cleanup_screenshot, take_screenshot
from .functions.system_status import system_status
from .functions.wsl_screenshot import wsl_screenshot, cleanup_wsl_screenshot, capture_zellij_sessions
from .functions.log_monitor import get_tails, format_log_message, get_logs_summary, format_log_results_for_telegram

load_dotenv()

# Configuração do logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramMonitor:
    """
    Classe para monitorar mensagens do Telegram e responder a triggers específicos.
    """

    def __init__(self, token: str, chat_id: str):
        """
        Inicializa o monitor do Telegram.

        Args:
            token: Token do bot do Telegram
            chat_id: ID do chat a ser monitorado
        """
        self.token = token
        self.chat_id = chat_id
        self.application = Application.builder().token(self.token).build()
        self.triggers: Dict[str, Callable] = {}

        # Registra os triggers padrão
        self._register_default_triggers()

    def _register_default_triggers(self):
        """Registra os triggers padrão do sistema."""
        # Trigger para o comando /ping
        self.application.add_handler(CommandHandler("ping", self._handle_ping))

        # Trigger para o comando /status
        self.application.add_handler(CommandHandler("status", self._handle_status))

        # Trigger para o comando /screenshot
        self.application.add_handler(
            CommandHandler("screenshot", self._handle_screenshot)
        )

        # Trigger para o comando /wsl_screenshot
        self.application.add_handler(
            CommandHandler("wsl_screenshot", self._handle_wsl_screenshot)
        )

        # Trigger para o comando /logs
        self.application.add_handler(
            CommandHandler("logs", self._handle_logs)
        )

        # Handler para mensagens em geral (para triggers customizados)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

    async def _handle_ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler para o comando /ping.
        Responde com 'Pong!' quando alguém envia /ping.
        """
        try:
            # Verifica se a mensagem veio do chat correto
            if str(update.effective_chat.id) == self.chat_id:
                response = ping_response()
                await update.message.reply_text(response)
                logger.info(
                    f"Respondido /ping do usuário {update.effective_user.first_name}"
                )
            else:
                logger.warning(
                    f"Comando /ping recebido de chat não autorizado: {update.effective_chat.id}"
                )

        except Exception as e:
            logger.error(f"Erro ao processar comando /ping: {e}")

    async def _handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler para o comando /status.
        Responde com informações do sistema.
        """
        try:
            # Verifica se a mensagem veio do chat correto
            if str(update.effective_chat.id) == self.chat_id:
                logger.info(
                    f"Comando /status solicitado por {update.effective_user.first_name}"
                )

                # Obtém status do sistema
                status_report = system_status()

                # Envia resposta (pode ser longa, então divide se necessário)
                await update.message.reply_text(status_report, parse_mode="Markdown")
                logger.info(
                    f"Status do sistema enviado para {update.effective_user.first_name}"
                )
            else:
                logger.warning(
                    f"Comando /status recebido de chat não autorizado: {update.effective_chat.id}"
                )

        except Exception as e:
            logger.error(f"Erro ao processar comando /status: {e}")
            # Envia mensagem de erro para o usuário
            try:
                await update.message.reply_text(
                    "❌ Erro ao obter status do sistema. Tente novamente."
                )
            except:
                pass

    async def _handle_screenshot(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handler para o comando /screenshot.
        Captura e envia screenshot da tela.
        """
        try:
            # Verifica se a mensagem veio do chat correto
            if str(update.effective_chat.id) == self.chat_id:
                logger.info(
                    f"Comando /screenshot solicitado por {update.effective_user.first_name}"
                )

                # Envia mensagem de aguarde
                await update.message.reply_text("📸 Capturando screenshot...")

                # Captura screenshot
                screenshot_path = take_screenshot()

                if screenshot_path:
                    try:
                        # Envia a imagem
                        with open(screenshot_path, "rb") as photo:
                            await update.message.reply_photo(
                                photo=photo, caption="📸 Screenshot capturada!"
                            )
                        logger.info(
                            f"Screenshot enviada para {update.effective_user.first_name}"
                        )
                    finally:
                        # Limpa o arquivo temporário
                        cleanup_screenshot(screenshot_path)
                else:
                    await update.message.reply_text(
                        "❌ Erro ao capturar screenshot. Verifique as dependências."
                    )
                    logger.error("Falha ao capturar screenshot")
            else:
                logger.warning(
                    f"Comando /screenshot recebido de chat não autorizado: {update.effective_chat.id}"
                )

        except Exception as e:
            logger.error(f"Erro ao processar comando /screenshot: {e}")
            # Envia mensagem de erro para o usuário
            try:
                await update.message.reply_text(
                    "❌ Erro ao capturar screenshot. Tente novamente."
                )
            except:
                pass

    async def _handle_wsl_screenshot(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler para o comando /wsl_screenshot.
        Captura screenshot usando WSL em diferentes cenários.
        """
        try:
            # Verifica se a mensagem veio do chat correto
            if str(update.effective_chat.id) == self.chat_id:
                logger.info(f"Comando /wsl_screenshot solicitado por {update.effective_user.first_name}")
                
                # Envia mensagem de aguarde
                await update.message.reply_text("🐧 Capturando screenshot via WSL...")
                
                # Captura screenshot via WSL
                screenshot_path = wsl_screenshot()
                
                if screenshot_path:
                    try:
                        # Verifica se o arquivo existe
                        if os.path.exists(screenshot_path):
                            # Envia a imagem
                            with open(screenshot_path, 'rb') as photo:
                                await update.message.reply_photo(
                                    photo=photo,
                                    caption="🐧 Screenshot WSL capturada!"
                                )
                            logger.info(f"Screenshot WSL enviada para {update.effective_user.first_name}")
                        else:
                            await update.message.reply_text("❌ Arquivo de screenshot não encontrado.")
                    except Exception as e:
                        logger.error(f"Erro ao enviar screenshot WSL: {e}")
                        await update.message.reply_text("❌ Erro ao enviar screenshot.")
                    finally:
                        # Limpa o arquivo temporário
                        cleanup_wsl_screenshot(screenshot_path)
                else:
                    # Tenta capturar informações do Zellij como alternativa
                    zellij_info = capture_zellij_sessions()
                    if zellij_info:
                        message = "❌ Screenshot WSL falhou, mas capturei info do Zellij:\n\n"
                        if 'sessions' in zellij_info:
                            message += f"**Sessões Ativas:**\n```\n{zellij_info['sessions']}\n```\n"
                        if 'layout' in zellij_info:
                            message += f"**Layout Atual:**\n```\n{zellij_info['layout'][:500]}...\n```"
                        await update.message.reply_text(message, parse_mode='Markdown')
                    else:
                        await update.message.reply_text(
                            "❌ Falha ao capturar screenshot WSL. Verifique:\n"
                            "• Se está rodando no WSL\n"
                            "• Se X11 ou Wayland estão configurados\n"
                            "• Se ferramentas de screenshot estão instaladas\n"
                            "• Se o Windows não está bloqueado"
                        )
                    logger.error("Falha ao capturar screenshot WSL")
            else:
                logger.warning(
                    f"Comando /wsl_screenshot recebido de chat não autorizado: {update.effective_chat.id}"
                )
                
        except Exception as e:
            logger.error(f"Erro ao processar comando /wsl_screenshot: {e}")
            # Envia mensagem de erro para o usuário
            try:
                await update.message.reply_text(
                    "❌ Erro ao capturar screenshot WSL. Tente novamente."
                )
            except:
                pass

    async def _handle_logs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler para o comando /logs.
        Busca e envia os últimos registros de log dos diretórios especificados.
        """
        try:
            # Verifica se a mensagem veio do chat correto
            if str(update.effective_chat.id) == self.chat_id:
                logger.info(f"Comando /logs solicitado por {update.effective_user.first_name}")
                
                # Envia mensagem de aguarde
                await update.message.reply_text("📋 Buscando logs dos diretórios...")
                
                # Primeiro, envia o resumo
                summary = get_logs_summary()
                await update.message.reply_text(summary)
                
                # Busca os logs
                logs = get_tails(15)  # Últimas 15 linhas de cada arquivo
                
                if not logs:
                    await update.message.reply_text("❌ Nenhum log encontrado.")
                    return
                
                # Formata as mensagens
                messages = format_log_results_for_telegram(logs)
                
                # Envia cada mensagem separadamente
                for message in messages:
                    try:
                        await update.message.reply_text(message)
                        
                        # Pequeno delay para evitar spam
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        # Se falhar, tenta enviar uma versão simplificada
                        try:
                            simple_message = f"❌ Erro ao enviar log: {str(e)}\n\n{message[:500]}..."
                            await update.message.reply_text(simple_message)
                        except:
                            await update.message.reply_text(
                                f"❌ Erro crítico ao enviar log: {str(e)}"
                            )
                
                logger.info(f"Logs enviados para {update.effective_user.first_name}")
                
            else:
                logger.warning(
                    f"Comando /logs recebido de chat não autorizado: {update.effective_chat.id}"
                )
                
        except Exception as e:
            logger.error(f"Erro ao processar comando /logs: {e}")
            # Envia mensagem de erro para o usuário
            try:
                await update.message.reply_text(
                    "❌ Erro ao buscar logs. Tente novamente."
                )
            except:
                pass

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handler para mensagens em geral.
        Loga todas as mensagens e processa triggers customizados.
        """
        try:
            # Verifica se a mensagem veio do chat correto
            if str(update.effective_chat.id) != self.chat_id:
                return

            user_name = update.effective_user.first_name or "Usuário"
            message_text = update.message.text

            # Loga a mensagem no terminal
            logger.info(f"[{user_name}]: {message_text}")

            # Processa triggers customizados
            message_lower = message_text.lower().strip()
            for trigger, handler in self.triggers.items():
                if trigger in message_lower:
                    await handler(update, context)
                    logger.info(f"Trigger '{trigger}' ativado por {user_name}")

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")

    async def start_monitoring(self):
        """
        Inicia o monitoramento das mensagens.
        Este método é bloqueante e deve ser executado em um loop asyncio.
        """
        try:
            logger.info("Iniciando monitoramento do Telegram...")
            logger.info(f"Monitorando chat ID: {self.chat_id}")

            # Inicia o bot
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()

            logger.info("Monitor do Telegram iniciado com sucesso!")

            # Mantém o bot rodando
            import signal

            # Cria evento para parar o bot
            stop_event = asyncio.Event()

            def signal_handler(signum, frame):
                stop_event.set()

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            # Aguarda o sinal para parar
            await stop_event.wait()

        except Exception as e:
            logger.error(f"Erro ao iniciar monitoramento: {e}")
            raise
        finally:
            await self.stop_monitoring()

    async def stop_monitoring(self):
        """Para o monitoramento das mensagens."""
        try:
            logger.info("Parando monitoramento do Telegram...")

            if self.application.updater.running:
                await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()

            logger.info("Monitor do Telegram parado com sucesso!")

        except Exception as e:
            logger.error(f"Erro ao parar monitoramento: {e}")
