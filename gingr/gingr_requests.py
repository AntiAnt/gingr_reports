import json
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List

import pandas as pd
import requests

from constants import GINGR_API_KEY, GINGR_ROOT_APP

DEFAULT_PACkAGE_TOTAL_CHARGE = 35.5


@dataclass
class Reservations:
    full_day_daycare_total: int
    full_day_daycare_daily_avg: float
    am_daycare_total: int
    am_daycare_daily_avg: float
    pm_daycare_total: int
    pm_daycare_daily_avg: float
    puppy_day_school_total: int
    puppy_day_school_daily_avg: float
    boarding_total: int
    boarding_daily_avg: float
    daycare_eval_total: int
    daycare_eval_daily_avg: float
    cancelled_total: int


class Package(Enum):
    DAY_20 = 35.5
    DA_10 = 39.563  # how transactions are described for 10 full day packages
    DA_5 = 41.4765  # Full day Daycare 5 day package
    PUPPY_SCHOOL_DAY = 95.715
    BOARDING = 63.85
    AM_DAYCARE = 32.97
    DAYCA_10 = 29.99  # AM Half-day daycare package of 10
    PM_DAYCARE = 32.97


class ReservationCode(Enum):
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

    def _get_num_weekdays(self, start_date: datetime, end_date: datetime) -> int:
        count = 0
        current_date = start_date

        while current_date <= end_date:
            print(current_date)
            if current_date.weekday() < 5:
                count += 1
            current_date += timedelta(days=1)

        return count

    def _map_to_reservation(self, reservation: Dict) -> ReservationCode:
        if reservation["id"] in ReservationCode._value2member_map_:
            return ReservationCode(reservation["id"])
        else:
            raise ValueError(
                f"This reservation type is currently not supported: {reservation}"
            )

    def get_reservations_by_service(
        self, start_date: str, end_date: str
    ) -> Reservations:
        num_days = (
            datetime.strptime(end_date, "%Y-%m-%d")
            - datetime.strptime(start_date, "%Y-%m-%d")
        ).days + 1
        num_weekdays = self._get_num_weekdays(
            start_date=datetime.strptime(start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(end_date, "%Y-%m-%d"),
        )
        res_df = self._get_reservations(start_date=start_date, end_date=end_date)

        df_reservation_type = pd.json_normalize(
            res_df["reservation_type"].apply(lambda x: x)
        )
        res_df = res_df.join(df_reservation_type)

        tot_cancelled_reservations = res_df[res_df["cancelled_date"].notna()].shape[0]

        reservation_total_counts = {
            "full_day_daycare_total": res_df[
                res_df["id"] == ReservationCode.FULL_DAY_DAYCARE.value
            ].shape[0],
            "am_daycare_total": res_df[
                res_df["id"] == ReservationCode.AM_DAYCARE.value
            ].shape[0],
            "pm_daycare_total": res_df[
                res_df["id"] == ReservationCode.PM_DAYCARE.value
            ].shape[0],
            "puppy_day_school_total": res_df[
                res_df["id"] == ReservationCode.PUPPY_DAY_SCHOOL.value
            ].shape[0],
            "boarding_total": res_df[
                res_df["id"] == ReservationCode.BOARDING.value
            ].shape[0],
            "daycare_eval_total": res_df[
                res_df["id"] == ReservationCode.DAYCARE_EVAL.value
            ].shape[0],
            "cancelled_total": tot_cancelled_reservations,
        }

        reservaton_averages = {
            "full_day_daycare_daily_avg": reservation_total_counts[
                "full_day_daycare_total"
            ]
            / num_weekdays,
            "am_daycare_daily_avg": reservation_total_counts["am_daycare_total"]
            / num_weekdays,
            "pm_daycare_daily_avg": reservation_total_counts["pm_daycare_total"]
            / num_weekdays,
            "puppy_day_school_daily_avg": reservation_total_counts[
                "puppy_day_school_total"
            ]
            / num_weekdays,
            "boarding_daily_avg": reservation_total_counts["boarding_total"] / num_days,
            "daycare_eval_daily_avg": reservation_total_counts["daycare_eval_total"]
            / num_weekdays,
        }

        reservation_counts = {**reservation_total_counts, **reservaton_averages}

        return Reservations(**reservation_counts)

    def get_reservations_revenue(self, start_date: str, end_date: str) -> pd.DataFrame:
        reservations = self._get_reservations(start_date=start_date, end_date=end_date)
        # filter out cancelled reservations
        filtered_reservations = reservations[
            reservations["cancelled_date"].isna()
            & (
                reservations["check_out_date"].notna()
                & (reservations["check_out_date"] != "")
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
            try:
                if reservation["transaction_id"] is None:
                    continue

                if reservation["reservation"] == ReservationCode.PUPPY_DAY_SCHOOL:
                    revenue += self._get_puppy_school_transaction_revenue(
                        transaction_id=int(reservation["transaction_id"])
                    )
                elif reservation["reservation"] == ReservationCode.BOARDING:
                    revenue += self._get_boarding_transaction_revenue(
                        transaction_id=int(reservation["transaction_id"])
                    )
                elif (
                    reservation["reservation"] == ReservationCode.FULL_DAY_DAYCARE
                    or reservation["reservation"] == ReservationCode.AM_DAYCARE
                    or reservation["reservation"] == ReservationCode.PM_DAYCARE
                ):
                    revenue += self._get_daycare_transaction_revenue(
                        transaction_id=int(reservation["transaction_id"])
                    )

            except Exception as e:
                raise Exception(
                    f"Error processing reservation with id: {reservation} . {e}"
                )
        return revenue

    def _get_boarding_transaction_revenue(self, transaction_id: int) -> float:
        transaction = self._get_transaction(transaction_id=transaction_id)[0]
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
        transaction = self._get_transaction(transaction_id=transaction_id)[0]

        if float(transaction["total"]) == 0.0:
            package_pattern = r"(\d{1,2}) \| ([A-Za-z]+) - (\d+) Remaining"
            # assume package
            desc: str = transaction["description"].strip()
            match = re.match(pattern=package_pattern, string=desc)

            if match is not None:
                total_units = match.group(1)
                package_type = match.group(2).upper()

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

    def _get_transaction(self, transaction_id) -> List[Dict]:
        get_url = f"https://{self.app_root}.gingrapp.com/api/v1/transaction"
        headers = {"Content-Type": "application/x-www-form-urlencoded; charset=utf-8"}
        data = {"key": self.api_key, "id": transaction_id}

        response = requests.post(get_url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()["data"]["items"]
        else:
            raise Exception(
                f"Error fetching POS figures: {response.status_code} {response.text}"
            )
