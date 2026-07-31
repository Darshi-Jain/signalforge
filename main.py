from __future__ import annotations
import argparse, json
from rich.console import Console
from rich.table import Table
from src.tools.customer_tools import CustomerRepository
from src.orchestration.investigation import investigate

console = Console()

def main():
    parser=argparse.ArgumentParser(description="Agentic Customer Intelligence MVP")
    sub=parser.add_subparsers(dest="command", required=True)
    inv=sub.add_parser("investigate"); inv.add_argument("--customer", required=True)
    scan=sub.add_parser("scan-portfolio"); scan.add_argument("--renewal-window", type=int, default=120)
    args=parser.parse_args(); repo=CustomerRepository()
    if args.command=="investigate":
        report=investigate(repo.get_account(args.customer)); console.print_json(report.model_dump_json(indent=2))
    else:
        reports=[investigate(repo.get_account(cid)) for cid in repo.list_customers()]
        reports=[r for r in reports if r.renewal_days <= args.renewal_window]
        reports.sort(key=lambda r:r.churn_probability*r.arr_at_risk, reverse=True)
        table=Table("Customer","Risk","Probability","ARR at risk","Renewal")
        for r in reports: table.add_row(r.customer_name,r.risk_level,f"{r.churn_probability:.0%}",f"${r.arr_at_risk:,.0f}",f"{r.renewal_days} days")
        console.print(table)
if __name__=="__main__": main()
