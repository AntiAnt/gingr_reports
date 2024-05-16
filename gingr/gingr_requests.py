import os
import pdb

import pandas as pd
import requests

from constants import GINGR_API_KEY, GINGR_ROOT_APP

class GingerRequests:
    def __init__(
        self, *, api_key: str | None = None, app_root: str | None = None
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv(GINGR_API_KEY)
        if self.api_key is None:
            raise ValueError("token is required for Gingr API. ")

        self.app_root = app_root if app_root is not None else os.getenv(GINGR_ROOT_APP)

        if self.app_root is None:
            raise ValueError("Root app name is required for Gingr API")

    def get_pos_figures(self, start_date=None, end_date=None) -> pd.DataFrame:
        get_url = f"https://{self.app_root}.gingrapp.com/api/v1/reservations"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8"
        }
        data = {
            "key": self.api_key,
            "start_date": "2024-04-01",
            "end_date": "2024-04-30"
        }

        response = requests.post(get_url, headers=headers, data=data)
        if response == 200:
            df = pd.DataFrame(response.json["data"].values())
            df.to_csv("output.csv")
            return df
        else:
            raise Exception(
                f"Error fetching POS figures: {response.status_code} {response.text}"
            )
