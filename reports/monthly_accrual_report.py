from dataclasses import asdict, dataclass
from datetime import date

from intuitlib.client import AuthClient

from app.accrual_report_db import get_accrual_reprot_record_manager
from gingr.gingr_reports import GingerReports
from intuit.quickbooks_service import QuickbooksServiceManager
from reports.reports import AccrualReport

accrual_report_manager = get_accrual_reprot_record_manager()



def get_monthly_acrual_report(
    intuit_auth_client: AuthClient, start_date: str, end_date: str | None = None
) -> AccrualReport | None:
    gingr = GingerReports()
    qb_sm = QuickbooksServiceManager(auth_client=intuit_auth_client)

    revenue = gingr.get_reservations_revenue(start_date=start_date, end_date=end_date)
    expenses = qb_sm.get_expenses_by_date_range(
        start_date=start_date, end_date=end_date
    )

    return accrual_report_manager.insert_report(
        AccrualReport(
            start_date=start_date,
            end_date=end_date,
            requested_on=date.today().isoformat(),
            revenue=revenue,
            expenses=expenses.total_expenses,
            net_profit=revenue - expenses.total_expenses,
            margin=((revenue - expenses.total_expenses) / revenue) * 100,
        )
    )
