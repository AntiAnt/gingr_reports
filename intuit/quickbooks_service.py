from typing import Dict

from intuitlib.client import AuthClient
from quickbooks import QuickBooks


class QuickbooksServiceManager:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

        self.qbo_client = QuickBooks(
            auth_client=self.auth_client,
            refresh_token=self.auth_client.refresh_token,
            company_id=self.auth_client.realm_id,
        )

    def get_expenses_by_date_range(
        self, start_date: str, end_date: str
    ) -> Dict[str, float]:
        company_info = self.qbo_client.get_report("profitandloss")
        return company_info
