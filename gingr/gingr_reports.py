import os
import pdb
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

import pandas as pd

from constants import GINGR_API_KEY, GINGR_ROOT_APP
from gingr.gingr_requests import GingerRequests

DEFAULT_PACkAGE_TOTAL_CHARGE = 35.5


@dataclass
class Owner:
    id: str
    first_name: str
    last_name: str
    animal_names: str
    cell_phone: str
    home_phone: str
    email: str
    address_1: str
    city: str
    state: str
    zip: str
    created_at: str
    created_by: str
    owner_created_at_iso: str
    home_location: str
    last_reservation: str
    number_reservations: str
    current_balance: str
    address_2: Optional[str] = None
    next_reservation: Optional[str] = None
    banned_animal_names: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class Owners:
    owners: List[Owner]


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
    DAYCAR_20 = 25.4  # AM Half-day daycare package of 20
    DAYCA_10 = 28.20  # AM Half-day daycare package of 10
    DAYCA_5 = 29.6  # AM Half-day daycare package of 5
    PM_DAYCARE = 32.97


class ReservationCode(Enum):
    FULL_DAY_DAYCARE = "1"
    AM_DAYCARE = "2"
    PM_DAYCARE = "9"
    PUPPY_DAY_SCHOOL = "6"
    BOARDING = "30"
    BOARDING_STANDARD = "32"
    PRIVATE_LESSON_SINGLE_SESSION = "28"
    DAYCARE_EVAL = (
        "7"  # TODO: filter these out earlier as they do not generate revenue ever.
    )
    GROUP_CLASS_BASIC_MANNERS = "11"
    BOARD_AND_TRAIN = "31"


class GingerReports:
    def __init__(
        self, *, api_key: str | None = None, app_root: str | None = None
    ) -> None:
        api_key = api_key if api_key is not None else os.getenv(GINGR_API_KEY)
        app_root = app_root if app_root is not None else os.getenv(GINGR_ROOT_APP)
        if api_key is None:
            raise ValueError("token is required for Gingr API. ")
        if app_root is None:
            raise ValueError("Root app name is required for Gingr API")

        self.requests = GingerRequests(api_key=api_key, app_root=app_root)

    def _get_num_weekdays(self, start_date: datetime, end_date: datetime) -> int:
        count = 0
        current_date = start_date

        while current_date <= end_date:
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

    def get_owners(self) -> Owners:
        return Owners(
            owners=[
                Owner(
                    id=o["id"],
                    first_name=o["first_name"],
                    last_name=o["last_name"],
                    animal_names=o["animal_names"],
                    cell_phone=o["cell_phone"],
                    home_phone=o["home_phone"],
                    email=o["email"],
                    address_1=o["address_1"],
                    city=o["city"],
                    state=o["state"],
                    zip=o["zip"],
                    created_at=o["created_at"],
                    created_by=o["created_by"],
                    owner_created_at_iso=o["owner_created_at_iso"],
                    home_location=o["home_location"],
                    last_reservation=o["last_reservation"],
                    next_reservation=o.get("next_reservation"),
                    number_reservations=o["number_reservations"],
                    current_balance=o["current_balance"],
                    address_2=o.get("address_2"),
                    banned_animal_names=o.get("banned_animal_names"),
                    notes=o.get("notes"),
                )
                for o in self.requests.get_owners()
            ]
        )

    def get_reservations_by_service(
        self, start_date: str, end_date: str
    ) -> Reservations:
        """Retrieves the number of reservations by service for a given date range"""
        num_days = (
            datetime.strptime(end_date, "%Y-%m-%d")
            - datetime.strptime(start_date, "%Y-%m-%d")
        ).days + 1
        num_weekdays = self._get_num_weekdays(
            start_date=datetime.strptime(start_date, "%Y-%m-%d"),
            end_date=datetime.strptime(end_date, "%Y-%m-%d"),
        )
        res_df = self.requests.get_reservations(
            start_date=start_date, end_date=end_date
        )

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
                or ReservationCode.BOARDING_STANDARD.value
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
        """Computes the revenue from reservations for a given date range.
        Range is limited to 30 days
        """
        reservations = pd.DataFrame(
            list(
                self.requests.get_reservations(start_date=start_date, end_date=end_date)
            )
        )
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
                pdb.set_trace()
                raise Exception(
                    f"Error processing reservation with id: {reservation} . {e}"
                )
        return revenue

    def _get_boarding_transaction_revenue(self, transaction_id: int) -> float:
        transaction = self.requests.get_transaction(transaction_id=transaction_id)[0]
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
        transaction = self.requests.get_transaction(transaction_id=transaction_id)[0]
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
