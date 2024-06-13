import os

from intuitlib.client import AuthClient

from gingr.gingr_requests import GingerRequests
from intuit.quickbooks_service import QuickbooksServiceManager


def get_monthly_acrual_report(
    intuit_auth_client: AuthClient, start_date: str, end_date: str | None = None
):

    gingr = GingerRequests()
    qb_sm = QuickbooksServiceManager(auth_client=intuit_auth_client)

    # rev = gingr.get_pos_revenue(start_date=start_date, end_date=end_date)
    # print(rev)

    expenses = qb_sm.get_expenses_by_date_range(
        start_date=start_date, end_date=end_date
    )
    print(expenses)
    return expenses
