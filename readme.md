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
- ✅ **Gestão de Banca** com meta diária de 5%
- ✅ **Janelas de Operação Alternadas** (manhã/noite)
- ✅ Armazena histórico permanente em **SQLite**
- ✅ Relatórios diários, mensais e análise de horários

---

## 🔄 Como Funciona

```
📩 Mensagem chega no Telegram
         
🔍 Parser extrai os sinais (horário, cor, número)
         
💾 Sinais salvos no SQLite + Agendados
         
🕐 Verifica janela de operação (manhã/noite)
         
💰 Verifica se meta diária foi atingida
         
⏰ Na hora certa → Aposta executada
         
📊 Resultado salvo + Banca atualizada
```

### Estratégia Martingale

| Entrada | Valor | Risco Acumulado |
|---------|-------|----------------|
| 1ª | 1% da banca | 1% |
| 2ª | 2% da banca | 3% |
| 3ª | 4% da banca | 7% |

- **WIN**: Para ao acertar a cor (lucro = 1% )
- **STOP LOSS**: Para após 3 tentativas (perda = 7%)

---

## 💰 Gestão de Banca

O bot possui um sistema inteligente de gestão de banca:

| Configuração | Valor Padrão | Descrição |
|--------------|--------------|------------|
| `BANK_INITIAL` | R$ 1000 | Banca inicial |
| `BANK_DAILY_GOAL_PERCENT` | 5% | Meta diária de lucro |
| `BANK_BET_PERCENT` | 1% | Valor da aposta base |

### Como funciona:

1. **Aposta base**: 1% da banca atual
2. **Meta diária**: 5% da banca atual
3. **Ao atingir a meta**: Bot para de operar até o dia seguinte
4. **Martingale**: 1% → 2% → 4% (máximo 7% de risco)

### Exemplo prático:

```
Banca: R$ 1000,00
Aposta base: R$ 10,00 (1%)
Meta do dia: R$ 50,00 (5%)

Após 4 wins: Lucro = R$ 50,00 ✅
→ Meta atingida! Bot pausa até amanhã.
```

---

## 🕐 Janelas de Operação

Baseado em análise de dados, o bot opera apenas nos melhores horários:

| Dia | Tipo | Janela | Taxa Histórica |
|-----|------|--------|----------------|
| Ímpares (1, 3, 5...) | Manhã | 07:00 - 11:00 | 100% |
| Pares (2, 4, 6...) | Noite | 20:00 - 23:00 | 100% |

### Por que alternar?

- Evita overtrading
- Opera apenas em horários com melhor performance
- Reduz exposição ao risco

### Verificar janela atual:

```bash
python report.py window
```

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
Windows:
python -m venv venv
venv\Scripts\activate

Linux/Mac:
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
# Telegram
API_ID=seu_api_id
API_HASH=seu_api_hash
SESSION_NAME=bet_session
SIGNAL_CHAT_TITLES=Nome do Grupo de Sinais

# Gestão de Banca
BANK_INITIAL=1000
BANK_DAILY_GOAL_PERCENT=50
BANK_BET_PERCENT=10
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

💰 Entrada 1º → 10=R$ PRETA
🎲 Resultado: VERMELHA - Nº 3

💰 Entrada 2º → 20=R$ PRETA
🎲 Resultado: PRETA - Nº 12

🎉 WIN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📁 Estrutura do Projeto

```
telegram-bet-bot/
│
├── main.py
├── report.py
├── migrate_to_sqlite.py
├── .env
├── requirements.txt
├── readme.md
│
├── data/
│   └── bot.db
│
└── app/
    ├── core/ 
    │   ├── strategy.py 
    │   └── bank_manager.py
    │
    ├── telegram/ 
    │   ├── telegram_listener.py
    │   └── signal_parser.py
    │
    ├── scheduler/ 
    │   └── scheduler.py
    │
    ├── executors/
    │   ├── executor_fake.py
    │   ├── executor_playwright.py
    │   └── executor_playwright_simulator.py
    │
    ├── extractors/
    │   └── double_result_extractor.py
    │
    ├── reports/
    │   └── daily_report.py
    │
    ├── shared/
    │   └── signal_queue.py
    │
    └── storage/
        ├── database.py
        ├── signal_store.py
        └── execution_store.py
```

---

## 🔧 Variáveis de Ambiente

### Telegram

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `API_ID` | ID da API do Telegram | *obrigatório* |
| `API_HASH` | Hash da API do Telegram | *obrigatório* |
| `SESSION_NAME` | Nome do arquivo de sessão | `bet_session` |
| `SIGNAL_CHAT_TITLES` | Nome(s) do grupo de sinais | - |
| `SIGNAL_CHAT_IDS` | ID(s) do grupo de sinais | - |

### Gestão de Banca

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `BANK_INITIAL` | Banca inicial em R$ | `1000` |
| `BANK_DAILY_GOAL_PERCENT` | Meta diária (%) | `50` |
| `BANK_BET_PERCENT` | Aposta base (%) | `10` |

### Sistema

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATA_DIR` | Diretório do banco de dados | `data` |

---

## 📊 Relatórios

O bot inclui um sistema completo de relatórios para acompanhar seus resultados.

### Comandos Disponíveis

```powershell
Relatório de hoje:
python report.py

Resumo de todos os dias:
python report.py all

Status da banca + janela de operação:
python report.py bank

Janela de operação atual:
python report.py window

Relatório mensal:
python report.py month
python report.py month 2026-01

Resetar banca:
python report.py reset        
python report.py reset 2000

Relatório de uma data específica:
python report.py 2026-01-08
```

### Exemplo de Relatório Diário

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RELATÓRIO DIÁRIO - 2026-01-07
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 RESUMO GERAL
   Total de sinais: 7
   ✅ WIN: 6
   ❌ LOSS: 0
   ⏭️  CANCELADOS: 1

🎯 TAXA DE ACERTO
   Apostas realizadas: 6
   Taxa de acerto: 100.0%

🎲 WINS POR TENTATIVA
   🥇 1ª entrada: 3
   🥈 2ª entrada: 2
   🥉 3ª entrada: 1

💰 RESULTADO FINANCEIRO
   🟢 LUCRO: +R$ 60.00

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Exemplo de Resumo Geral

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RESUMO GERAL - TODOS OS DIAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📅 2026-01-05 | 🟢 +R$ 50.00
   WIN: 5 | LOSS: 0 | CANCEL: 1 | Taxa: 100.0%

📅 2026-01-06 | 🔴 -R$ 70.00
   WIN: 21 | LOSS: 4 | CANCEL: 11 | Taxa: 84.0%

📅 2026-01-07 | 🟢 +R$ 60.00
   WIN: 6 | LOSS: 0 | CANCEL: 1 | Taxa: 100.0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 TOTAL ACUMULADO
   Sinais: 49 | Apostas: 36
   WIN: 32 | LOSS: 4 | CANCEL: 13
   Taxa de acerto: 88.9%
   🟢 LUCRO TOTAL: +R$ 40.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Cálculo de Lucro/Prejuízo

O relatório calcula automaticamente baseado na estratégia Martingale:

| Resultado | Valor (base R$ 100) |
|-----------|---------------------|
| WIN (qualquer entrada) | +1% = +R$ 10,00 |
| LOSS (stop loss) | -7% = -R$ 70,00 |
| CANCELLED | R$ 0,00 |

> **Nota**: Os valores são proporcionais à banca. Com banca de R$ 2000, o WIN seria +R$ 20 e LOSS seria -R$ 140.

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


