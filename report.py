import sys
from datetime import datetime
from app.reports.daily_report import print_daily_report, print_summary_all_days
from app.core.bank_manager import print_status as print_bank_status, reset_bank, print_monthly_report, get_window_status


def print_window_info():
    """Mostra informações sobre a janela de operação"""
    window = get_window_status()
    
    sep = "━" * 45
    print(f"\n{sep}")
    print(f"🕐 JANELA DE OPERAÇÃO - DIA {window['day']}")
    print(sep)
    
    print(f"\n   Tipo: {window['window_type']}")
    print(f"   Horário: {window['start']} às {window['end']}")
    print(f"   Hora atual: {window['current_time']}")
    
    if window['is_active']:
        print(f"\n   ✅ JANELA ATIVA - Bot operando!")
    else:
        print(f"\n   ⏸️  FORA DA JANELA - Sinais serão ignorados")
    
    print(f"\n📅 CALENDÁRIO DE JANELAS:")
    print(f"   Dias Ímpares (1, 3, 5...): Manhã 07:00-11:00")
    print(f"   Dias Pares (2, 4, 6...):   Noite 20:00-23:00")
    
    print(f"\n{sep}\n")


def main():
    if len(sys.argv) < 2:
        print_daily_report()
    elif sys.argv[1] == "all":
        print_summary_all_days()
    elif sys.argv[1] == "bank":
        print_bank_status()
    elif sys.argv[1] == "window":
        print_window_info()
    elif sys.argv[1] == "month":
        if len(sys.argv) > 2:
            try:
                month_str = sys.argv[2]
                if "-" in month_str:
                    year, month = map(int, month_str.split("-"))
                elif "/" in month_str:
                    month, year = map(int, month_str.split("/"))
                else:
                    raise ValueError("Formato inválido")
                print_monthly_report(year, month)
            except ValueError:
                print(f"❌ Formato inválido: {sys.argv[2]}")
                print("   Use: 2026-01 ou 01/2026")
        else:
            print_monthly_report()
    elif sys.argv[1] == "reset":
        if len(sys.argv) > 2:
            try:
                new_value = float(sys.argv[2])
                reset_bank(new_value)
                print(f"✅ Banca resetada para R$ {new_value:.2f}")
            except ValueError:
                print(f"❌ Valor inválido: {sys.argv[2]}")
        else:
            reset_bank()
            print("✅ Banca resetada para o valor padrão")
        print_bank_status()
    else:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            print_daily_report(target_date)
        except ValueError:
            print(f"❌ Comando inválido: {sys.argv[1]}")
            print("\nComandos disponíveis:")
            print("   python report.py             # Relatório de hoje")
            print("   python report.py all         # Todos os dias")
            print("   python report.py bank        # Status da banca")
            print("   python report.py window      # Janela de operação atual")
            print("   python report.py month       # Relatório do mês atual")
            print("   python report.py month 2026-01  # Relatório de janeiro/2026")
            print("   python report.py reset       # Resetar banca (padrão)")
            print("   python report.py reset 150   # Resetar banca para R$ 150")
            print("   python report.py 2026-01-06  # Data específica")


if __name__ == "__main__":
    main()
