import os

from gingr.gingr_requests import GingerRequests
from intuit.quickbooks_service import QuickbooksServiceManager


def main():
    start_date = "2024-03-01"
    end_date = "2024-03-31"
    gingr = GingerRequests()
    qb_sm = QuickbooksServiceManager()

    # rev = gingr.get_pos_revenue(start_date=start_date, end_date=end_date)
    # print(rev)

    expenses = qb_sm.get_expenses_by_date_range(
        start_date=start_date, end_date=end_date
    )
    print(expenses)
