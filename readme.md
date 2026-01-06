Mensagem chega
↓
Parser extrai N sinais
↓
Cada sinal:
   - é salvo no JSON do dia
   - é agendado
↓
Na hora certa:
   - aposta executada
   - sinal marcado como EXECUTADO
   - removido do JSON (ou flag)
↓
Novo dia:
   - cria novo JSON
   - ignora arquivo antigo


arquitetura

telegram-bet-bot/
│
├─ main.py
├─ .env
├─ bet.session.session
├─ readme.md
│
├─ data/                     ← DADOS (JSON / DB) (configurável via env `DATA_DIR`)
│   ├─ signals.json
│   └─ executions.json
│
├─ app/
│   ├─ __init__.py
│   │
│   ├─ core/                 ← REGRAS DE NEGÓCIO
│   │   ├─ __init__.py
│   │   └─ strategy.py
│   │
│   ├─ telegram/             ← TELEGRAM
│   │   ├─ __init__.py
│   │   ├─ telegram_listener.py
│   │   └─ signal_parser.py
│   │
│   ├─ scheduler/            ← AGENDAMENTO
│   │   ├─ __init__.py
│   │   └─ scheduler.py
│   │
│   ├─ executors/            ← EXECUÇÃO (fake / real)
│   │   ├─ __init__.py
│   │   ├─ executor_fake.py
│   │   └─ executor_playwright.py
│   │
│   └─ storage/              ← PERSISTÊNCIA
│       ├─ __init__.py
│       ├─ signal_store.py
│       └─ execution_store.py
│
└─ venv/

Nota: por padrão os arquivos de dados (`signals.json`, `executions.json`) são gravados em `data/`.
Você pode alterar o diretório definindo a variável de ambiente `DATA_DIR` antes de executar a aplicação.

Exemplos:
- PowerShell: `set DATA_DIR=storage; python main.py`
- Bash: `DATA_DIR=storage python main.py`

Retenção de dados:
- Por padrão os arquivos mantêm dados dos últimos **3 dias**; isso é configurável via a variável de ambiente `DATA_RETENTION_DAYS`.
   - PowerShell: `set DATA_RETENTION_DAYS=5`  (mantém 5 dias)
