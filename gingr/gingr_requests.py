from typing import Dict, List

import requests


class GingerRequests:
    def __init__(self, *, api_key: str, app_root: str) -> None:
        self.api_key = api_key
        self.app_root = app_root

    def get_reservations(self, start_date, end_date) -> List:
        """Maximum date range is 30 days"""
        url = f"https://{self.app_root}.gingrapp.com/api/v1/reservations"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        data = {"key": self.api_key, "start_date": start_date, "end_date": end_date}

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()["data"].values()
        else:
            raise Exception(
                f"Error fetching POS figures: {response.status_code} {response.text}"
            )

    def get_transaction(self, transaction_id) -> List[Dict]:
        url = f"https://{self.app_root}.gingrapp.com/api/v1/transaction"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        data = {"key": self.api_key, "id": transaction_id}

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()["data"]["items"]
        else:
            raise Exception(
                f"Error fetching POS figures: {response.status_code} {response.text}"
            )

    def get_owners(self, param: List | None = None) -> List:
        url = f"https://{self.app_root}.gingrapp.com/api/v1/owners"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        data = {"key": self.api_key}

        response = requests.post(url=url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()["data"]
        else:
            raise Exception(
                f"Error fetching owners: {response.status_code} {response.text}"
            )
