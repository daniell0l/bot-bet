# 🤖 Telegram Bet Bot

Bot automatizado para receber sinais de apostas via Telegram e executar apostas automáticas no jogo Double usando estratégia Martingale.

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Como Funciona](#-como-funciona)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Variáveis de Ambiente](#-variáveis-de-ambiente)

---

## ✨ Funcionalidades

- ✅ Recebe sinais automaticamente de grupos/canais do Telegram
- ✅ Detecta edições de mensagens e cancela entradas alteradas
- ✅ Agenda apostas para o horário exato do sinal
- ✅ Executa apostas usando estratégia Martingale
- ✅ Suporta sinais após meia-noite (dia seguinte)
- ✅ Armazena histórico de sinais e execuções
- ✅ Limpeza automática de dados antigos

---

## 🔄 Como Funciona

```
📩 Mensagem chega no Telegram
         
🔍 Parser extrai os sinais (horário, cor, número)
         
💾 Sinais salvos no JSON + Agendados
         
⏰ Na hora certa → Aposta executada
         
📊 Resultado salvo (WIN/LOSS/CANCELLED)
```

### Estratégia Martingale

| Entrada | Valor |
|---------|-------|
| 1ª | R$ 5 |
| 2ª | R$ 10 |
| 3ª | R$ 20 |

- **WIN**: Para ao acertar a cor
- **STOP LOSS**: Para após 3 tentativas

---

## 📦 Pré-requisitos

- Python 3.10+
- Conta no Telegram com API ID e Hash
- Navegador Chromium (instalado via Playwright)

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/daniell0l/bot-bet.git
cd bot-bet
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Instale o navegador do Playwright

```bash
playwright install chromium
```

---

## ⚙️ Configuração

### 1. Crie o arquivo `.env`

```env
API_ID=seu_api_id
API_HASH=seu_api_hash
SESSION_NAME=bet_session
SIGNAL_CHAT_TITLES=Nome do Grupo de Sinais
```

### 2. Obtenha suas credenciais do Telegram

1. Acesse [my.telegram.org](https://my.telegram.org)
2. Faça login com seu número
3. Vá em "API development tools"
4. Copie o `API_ID` e `API_HASH`

### 3. Configure o grupo de sinais

Use **uma** das opções no `.env`:

```env
# Por nome do grupo
SIGNAL_CHAT_TITLES=Seu Grupo de Sinais

# Ou por ID do grupo
SIGNAL_CHAT_IDS=-ID do Grupo
```

---

## ▶️ Uso

### Executar o bot

```bash
python main.py
```

### Primeira execução

Na primeira vez, o Telegram pedirá:
1. Número de telefone
2. Código de verificação (SMS ou app)

Após isso, a sessão é salva e não pedirá novamente.

### Saída esperada

```
🤖 Telegram conectado
🌐 Página do Double carregada

📩 NOVA MENSAGEM DETECTADA (Nome do Grupo)
────────────────────────────
✅ SINAL SALVO
🕒 Horário: 22:30
🎯 Cor: PRETA
🔢 Número: 12
────────────────────────────

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 SINAL 22:30 | PRETA
🆔 221c8459
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👀 Observação
⏭️ Rodada descartada: 7 | VERMELHA
🎲 Observação válida: 1 | VERMELHA

💰 Entrada 1º → 5=R$ PRETA
🎲 Resultado: VERMELHA - Nº 3

💰 Entrada 2º → 10=R$ PRETA
🎲 Resultado: PRETA - Nº 12

🎉 WIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📁 Estrutura do Projeto

```
telegram-bet-bot/
│
├── main.py                 # Ponto de entrada
├── .env                    # Variáveis de ambiente
├── requirements.txt        # Dependências
├── readme.md
│
├── data/                   # Dados persistidos
│   ├── signals.json        # Sinais recebidos
│   └── executions.json     # Histórico de execuções
│
└── app/
    ├── core/               # Regras de negócio
    │   └── strategy.py     # Estratégia Martingale
    │
    ├── telegram/           # Integração Telegram
    │   ├── telegram_listener.py
    │   └── signal_parser.py
    │
    ├── scheduler/          # Agendamento
    │   └── scheduler.py
    │
    ├── executors/          # Execução de apostas
    │   ├── executor_fake.py
    │   ├── executor_playwright.py
    │   └── executor_playwright_simulator.py
    │
    ├── extractors/         # Extração de resultados
    │   └── double_result_extractor.py
    │
    ├── shared/             # Recursos compartilhados
    │   └── signal_queue.py
    │
    └── storage/            # Persistência de dados
        ├── signal_store.py
        └── execution_store.py
```

---

## 🔧 Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `API_ID` | ID da API do Telegram | *obrigatório* |
| `API_HASH` | Hash da API do Telegram | *obrigatório* |
| `SESSION_NAME` | Nome do arquivo de sessão | `bet_session` |
| `SIGNAL_CHAT_TITLES` | Nome(s) do grupo de sinais | - |
| `SIGNAL_CHAT_IDS` | ID(s) do grupo de sinais | - |
| `DATA_DIR` | Diretório dos dados | `data` |
| `DATA_RETENTION_DAYS` | Dias para manter histórico | `3` |

### Exemplos de uso

```powershell
# Windows PowerShell
$env:DATA_DIR="storage"; python main.py
$env:DATA_RETENTION_DAYS="7"; python main.py
```

```bash
# Linux/Mac
DATA_DIR=storage python main.py
DATA_RETENTION_DAYS=7 python main.py
```

---

## 📝 Formato de Sinais Suportados

O bot reconhece mensagens no formato: 

ajuste de acordo ao seu...

```
💰 22:30 entrar na PRETA, vai cair número (12)
💰 22:48 entrar na PRETA, vai cair número (9)
💰 23:00 entrar na VERMELHA, vai cair número (1)
```

---

## ⚠️ Aviso Legal

Este bot é apenas para fins educacionais. O uso de bots para apostas pode violar os termos de serviço de algumas plataformas. Use por sua conta e risco.

---

## 📄 Licença

MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

