import os
import re
from enum import Enum
from typing import Dict

import pandas as pd
import requests

from constants import GINGR_API_KEY, GINGR_ROOT_APP

DEFAULT_PACkAGE_TOTAL_CHARGE = 35.5


class Package(Enum):
    DAY_20 = 35.5
    DAY_10 = 39.563
    DAY_5 = 41.4765
    PUPPY_SCHOOL_DAY = 95.715
    BOARDING = 63.85
    AM_DAYCARE = 32.97
    PM_DAYCARE = 32.97


class Reservation(Enum):
    FULL_DAY_DAYCARE = "1"
    AM_DAYCARE = "2"
    PM_DAYCARE = "9"
    PUPPY_DAY_SCHOOL = "6"
    BOARDING = "30"
    DAYCARE_EVAL = (
        "7"  # TODO: filter these out earlier as they do not generate revenue ever.
    )


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

    def _map_to_reservation(self, reservation: Dict) -> Reservation:
        if reservation["id"] in Reservation._value2member_map_:
            return Reservation(reservation["id"])
        else:
            raise ValueError(
                f"This reservation type is currently not supported: {reservation}"
            )

    def get_pos_revenue(self, start_date: str, end_date: str) -> pd.DataFrame:
        reservations = self._get_reservations(start_date=start_date, end_date=end_date)

        # filter out cancelled reservations
        filtered_reservations = reservations[
            (
                reservations["cancelled_date"].isna()
                | (reservations["cancelled_date"] == "")
            )
            & (
                reservations["check_out_date"].notna()
                | (reservations["check_out_date"] != "")
            )
        ]

        filtered_reservations["owner_id"] = filtered_reservations["owner"].apply(
            lambda x: x.get("id")
        )
        filtered_reservations["transaction_id"] = (
            filtered_reservations["transaction"]
            .apply(
                lambda x: x.get("pos_transaction_id") if isinstance(x, dict) else None
            )
            .astype("object")
        )
        filtered_reservations["reservation"] = filtered_reservations[
            "reservation_type"
        ].apply(self._map_to_reservation)
        reduced_reservations = filtered_reservations[
            ["reservation_id", "reservation", "owner_id", "transaction_id"]
        ]

        print(f"Number of filtered reservations: {len(reservations)}")

        return self._sum_revenue(reduced_reservations)

    def _get_reservations(self, start_date, end_date) -> pd.DataFrame:
        """Maximum date range is 30 days"""

        get_url = f"https://{self.app_root}.gingrapp.com/api/v1/reservations"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        data = {"key": self.api_key, "start_date": start_date, "end_date": end_date}

        response = requests.post(get_url, headers=headers, data=data)
        if response.status_code == 200:
            return pd.DataFrame(response.json()["data"].values())
        else:
            raise Exception(
                f"Error fetching POS figures: {response.status_code} {response.text}"
            )

    def _sum_revenue(self, reservations_df: pd.DataFrame) -> float:
        revenue = 0.0
        for _, reservation in reservations_df.iterrows():
            if reservation["transaction_id"] is None:
                continue

            if reservation["reservation"] == Reservation.PUPPY_DAY_SCHOOL:
                revenue += self._get_puppy_school_transaction_revenue(
                    transaction_id=int(reservation["transaction_id"])
                )
            elif reservation["reservation"] == Reservation.BOARDING:
                revenue += self._get_boarding_transaction_revenue(
                    transaction_id=int(reservation["transaction_id"])
                )
            elif (
                reservation["reservation"] == Reservation.FULL_DAY_DAYCARE
                or reservation["reservation"] == Reservation.AM_DAYCARE
                or reservation["reservation"] == Reservation.PM_DAYCARE
            ):
                revenue += self._get_daycare_transaction_revenue(
                    transaction_id=int(reservation["transaction_id"])
                )

        return revenue

    def _get_boarding_transaction_revenue(self, transaction_id: int) -> float:
        transaction = self._get_transaction(transaction_id=transaction_id)
        total_charges = float(transaction["total"]) + float(transaction["tax_amount"])

        if (
            transaction["refund_amount"] is not None
            and float(transaction["refund_amount"]) > 0.0
        ):
            total_charges -= float(transaction["refund_amount"]) + float(
                transaction["tax_refund_amount"]
            )

        return total_charges

    def _get_puppy_school_transaction_revenue(self, transaction_id: int) -> float:
        return Package.PUPPY_SCHOOL_DAY.value

    def _get_daycare_transaction_revenue(self, transaction_id: int) -> float:
        transaction = self._get_transaction(transaction_id=transaction_id)

        if float(transaction["total"]) == 0.0:
            package_pattern = r"(\d{1,2}) \| ([A-Za-z]+) - (\d+) Remaining"
            # assume package
            desc: str = transaction["description"].strip()
            match = re.match(pattern=package_pattern, string=desc)

            if match is not None:
                total_units = match.group(1)
                package_type = (
                    match.group(2).upper()
                    if match.group(2).lower() == "day"
                    else match.group(2).upper() + "Y"
                )

                return Package[f"{package_type}_{total_units}"].value

        total_charges = float(transaction["total"]) + float(transaction["tax_amount"])

        if (
            transaction["refund_amount"] is not None
            and float(transaction["refund_amount"]) > 0.0
        ):
            total_charges -= float(transaction["refund_amount"]) + float(
                transaction["tax_refund_amount"]
            )

        if total_charges == 0.0:
            total_charges = DEFAULT_PACkAGE_TOTAL_CHARGE

        return total_charges

    def _get_transaction(self, transaction_id) -> float:
        get_url = f"https://{self.app_root}.gingrapp.com/api/v1/transaction"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        data = {"key": self.api_key, "id": transaction_id}

        response = requests.post(get_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()["data"]["items"][0]
        else:
            raise Exception(
                f"Error fetching POS figures: {response.status_code} {response.text}"
            )
