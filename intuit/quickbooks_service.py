import os
import pdb
from typing import Dict
from urllib.parse import parse_qs, urlparse

from intuitlib.client import AuthClient
from intuitlib.enums import Scopes
from quickbooks import QuickBooks

from constants import (
    INTUIT_ACCESS_TOKEN,
    INTUIT_CLIENT_ID,
    INTUIT_CLIENT_SECRET,
    INTUIT_REALM_ID,
)


class QuickbooksServiceManager:
    def __init__(
        self,
        *,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
        realm_id: str | None = None
    ):
        self.client_id = (
            client_id if client_id is not None else os.getenv(INTUIT_CLIENT_ID)
        )
        self.client_secret = (
            client_secret
            if client_secret is not None
            else os.getenv(INTUIT_CLIENT_SECRET)
        )
        self.access_token = (
            access_token if access_token is not None else os.getenv(INTUIT_ACCESS_TOKEN)
        )
        self.realm_id = realm_id if realm_id is not None else os.getenv(INTUIT_REALM_ID)

        self.qbo_client = self._init_quickbooks_online_client()
        pdb.set_trace()

    def _init_quickbooks_online_client(self):
        auth_client = AuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token=self.access_token,
            environment="sandbox",
            redirect_uri="https://developer.intuit.com/v2/OAuth2Playground/RedirectUrl",
        )
        params = parse_qs(urlparse(auth_client.get_authorization_url(scopes=[Scopes.ACCOUNTING])).query)
        pdb.set_trace()
        auth_client.get_bearer_token(auth_code="")

        client = QuickBooks(
            auth_client=auth_client,
            refresh_token=auth_client.refresh_token,
            company_id=self.realm_id,
        )

        return client

    def get_expenses_by_date_range(start_date: str, end_date: str) -> Dict[str, float]:
        pass
