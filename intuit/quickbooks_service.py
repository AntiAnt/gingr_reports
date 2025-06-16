import json
from dataclasses import dataclass
from typing import Dict, List

import requests
from intuitlib.client import AuthClient
from quickbooks import QuickBooks


@dataclass
class ExpenseReport:
    start_date: str
    end_date: str
    requested_datetime: str
    currency: str
    expenses: List[Dict[str, float]]
    total_expenses: float

    @classmethod
    def get_report_from_response_json(cls, response_dict: Dict) -> "ExpenseReport":
        expenses = []
        total_expenses = None

        # assumes only one section for expenses
        for row in response_dict["Rows"]["Row"]:
            if row.get("group") == "Expenses":
                total_expenses = float(row["Summary"]["ColData"][1]["value"])
                for _expenses in row["Rows"]["Row"]:
                    if "Header" in _expenses: # TODO: this is a band aid figure out why this header comes up
                        _expenses = _expenses["Header"]
                    expenses.append(
                        {
                            "title": _expenses["ColData"][0]["value"],
                            "cost": float(_expenses["ColData"][1]["value"]),
                        }
                    )

        return cls(
            start_date=response_dict["Header"]["StartPeriod"],
            end_date=response_dict["Header"]["EndPeriod"],
            requested_datetime=response_dict["Header"]["Time"],
            currency=response_dict["Header"]["Currency"],
            expenses=expenses,
            total_expenses=total_expenses,
        )


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
    ) -> ExpenseReport:
        base_url = f"https://quickbooks.api.intuit.com/v3/company/{self.auth_client.realm_id}/reports/ProfitAndLoss"
        headers = {
            "Authorization": f"Bearer {self.auth_client.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        params = {"start_date": start_date, "end_date": end_date}

        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200:
            return ExpenseReport.get_report_from_response_json(
                response_dict=response.json()
            )
        else:
            raise Exception(
                f"Error: {response.status_code}\nContext: {response.json()}"
            )
