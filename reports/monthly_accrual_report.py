import calendar
from dataclasses import asdict, dataclass
from datetime import date
from typing import Dict
import json

from intuitlib.client import AuthClient

from app.accrual_report_db import get_accrual_reprot_record_manager
from gingr.gingr_reports import GingerReports
from intuit.quickbooks_service import QuickbooksServiceManager
from reports.reports import AccrualReport

accrual_report_manager = get_accrual_reprot_record_manager()


def _create_accrual_report(
    intuit_auth_client: AuthClient, start_date: str, end_date: str | None = None
) -> AccrualReport:
    gingr = GingerReports()
    qb_sm = QuickbooksServiceManager(auth_client=intuit_auth_client)
    print(f"Creating Accrual Report, start date: {start_date}, end date: {end_date}")
    reservations_breakdown, revenue = gingr.get_reservations_revenue(
        start_date=start_date, end_date=end_date
    )
    expenses = qb_sm.get_expenses_by_date_range(
        start_date=start_date, end_date=end_date
    )
    return AccrualReport(
        start_date=start_date,
        end_date=end_date,
        requested_on=date.today().isoformat(),
        revenue=revenue,
        expenses=expenses.total_expenses,
        net_profit=revenue - expenses.total_expenses,
        number_reservations=reservations_breakdown["total_reservations"],
        margin=((revenue - expenses.total_expenses) / revenue) * 100,
        expense_report=json.dumps(expenses.expenses),
        reservations_report=json.dumps(reservations_breakdown)
    )


def get_monthly_acrual_report(
    intuit_auth_client: AuthClient, start_date: str, end_date: str | None = None
) -> AccrualReport | None:
    report = accrual_report_manager.get_report_by_start_and_end_date(start_date=start_date, end_date=end_date)
    if report is None:
        report = _create_accrual_report(
            intuit_auth_client=intuit_auth_client, start_date=start_date, end_date=end_date
        )
        print(f"saving report, start date:{start_date}, end date:{end_date}")
        return accrual_report_manager.insert_report(report=report)

    return report


def generate_current_month_accrual_reprort(
    current_date: date, intuit_auth_client: AuthClient
) -> Dict[int, AccrualReport]:
    return _create_accrual_report(
        intuit_auth_client=intuit_auth_client,
        start_date=date(
            year=current_date.year, month=current_date.month, day=1
        ).isoformat(),
        end_date=current_date.isoformat(),
    )


def generate_ytd_historic_monthly_accrual_reports(
    year: int,
    monthly_accrual_reports: Dict[int, AccrualReport],
    intuit_auth_client: AuthClient,
    range_month_start: int = 1,
    range_month_end: int = 12,
) -> Dict[int, AccrualReport]:
    reports_not_saved = set(range(range_month_start, range_month_end + 1)) - set(
        monthly_accrual_reports.keys()
    )

    for month in reports_not_saved:
        start_date_iso_str = date(year=year, month=month, day=1).isoformat()
        end_date_iso_str = date(
            year=year, month=month, day=calendar.monthrange(year=year, month=month)[-1]
        ).isoformat()

        monthly_accrual_reports[month] = asdict(
            get_monthly_acrual_report(
                start_date=start_date_iso_str,
                end_date=end_date_iso_str,
                intuit_auth_client=intuit_auth_client,
            )
        )
    return monthly_accrual_reports


def get_ytd_historic_monthly_accrual_reports(year: int) -> Dict[int, AccrualReport]:
    historic_monthly_reports = accrual_report_manager.get_all_monthly_reports_by_year(
        year
    )
    return {
        date.fromisoformat(report.start_date).month: asdict(report)
        for report in historic_monthly_reports
    }
