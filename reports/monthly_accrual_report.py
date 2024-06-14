from dataclasses import dataclass

from intuitlib.client import AuthClient

from gingr.gingr_reports import GingerReports
from intuit.quickbooks_service import QuickbooksServiceManager


@dataclass
class AccrualReport:
    revenue: float
    expenses: float
    net_profit: float
    margin: float


def get_monthly_acrual_report(
    intuit_auth_client: AuthClient, start_date: str, end_date: str | None = None
):
    gingr = GingerReports()
    qb_sm = QuickbooksServiceManager(auth_client=intuit_auth_client)

    revenue = gingr.get_reservations_revenue(start_date=start_date, end_date=end_date)
    expenses = qb_sm.get_expenses_by_date_range(
        start_date=start_date, end_date=end_date
    )

    return AccrualReport(
        revenue=revenue,
        expenses=expenses.total_expenses,
        net_profit=revenue - expenses.total_expenses,
        margin=((revenue - expenses.total_expenses) / revenue) * 100,
    )
