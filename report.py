import sys
from datetime import datetime
from app.reports.daily_report import print_daily_report, print_summary_all_days


def main():
    if len(sys.argv) < 2:
        print_daily_report()
    elif sys.argv[1] == "all":
        print_summary_all_days()
    else:
        try:
            target_date = datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
            print_daily_report(target_date)
        except ValueError:
            print(f"❌ Data inválida: {sys.argv[1]}")
            print("   Use o formato: YYYY-MM-DD (ex: 2026-01-07)")
            print("\nExemplos:")
            print("   python report.py           # Hoje")
            print("   python report.py all       # Todos os dias")
            print("   python report.py 2026-01-06  # Data específica")


if __name__ == "__main__":
    main()
