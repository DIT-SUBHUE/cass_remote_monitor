# Cass Remote Monitor

Monitor de mensagens do Telegram que responde a triggers específicos.

## Estrutura do Projeto

```
cass_remote_monitor/
├── .env                         # Configurações do bot
├── requirements.txt             # Dependências
├── start.py                    # Script principal
├── modules/
│   ├── telegram_logger.py      # Módulo de logging
│   ├── telegram_monitor.py     # Módulo de monitoramento
│   └── functions/              # Funções utilitárias
│       ├── __init__.py
│       ├── ping.py            # Função /ping
│       ├── system_status.py   # Função /status
│       ├── screenshot.py      # Função /screenshot
│       └── wsl_screenshot.py  # Função /wsl_screenshot
```

## Configuração

1. Configure as variáveis de ambiente no arquivo `.env`:
```env
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute o monitor:
```bash
python start.py
```

## Comandos Disponíveis

- `/ping` - Responde com "Pong! 🏓"
- `/status` - Mostra informações detalhadas do sistema:
  - Informações gerais (usuário, OS, arquitetura)
  - Status do processador (núcleos, uso, frequência)
  - Status da memória RAM (total, usado, disponível)
  - Status do armazenamento (total, usado, livre)
  - Redes conectadas (WiFi, Ethernet, etc.)
  - Status do processador (núcleos, uso, frequência)
  - Status da memória RAM (total, usado, disponível)
  - Status do armazenamento (total, usado, livre)
  - Redes conectadas (WiFi, Ethernet, etc.)
- `/screenshot` - Captura e envia screenshot da tela:
  - Suporte multiplataforma (Windows/Linux/macOS)
  - Remoção automática de arquivos temporários
  - Detecção automática de dependências disponíveis
- `/wsl_screenshot` - Captura screenshot via WSL:
  - Funciona mesmo com Windows bloqueado
  - Detecta automaticamente WSL vs Windows
  - Suporte a X11 e Wayland
  - Fallback para informações do Zellij
  - Múltiplos métodos de captura (scrot, gnome-screenshot, ImageMagick, etc.)

## Características

- ✅ Monitora apenas o chat configurado
- ✅ Loga todas as mensagens no terminal
- ✅ Suporte multiplataforma (Windows/Linux)
- ✅ Tratamento de erros robusto
- ✅ Arquitetura modular para fácil extensão

## Adicionando Novas Funções

Para adicionar uma nova função:

1. Crie um arquivo `.py` em `modules/functions/`
2. Implemente sua função
3. Adicione o import no `__init__.py`
4. Adicione o handler no `telegram_monitor.py`

Para parar o monitor, pressione `Ctrl+C`.