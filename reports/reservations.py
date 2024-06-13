from datetime import datetime, timedelta

import pytz

from gingr.gingr_requests import GingerRequests, Reservations

date_format = "%Y-%m-%d"


def get_reservations_by_service_for_the_week() -> Reservations:
    end_date = datetime.now(tz=pytz.utc).date()
    start_date = end_date - timedelta(days=end_date.weekday() + 1)

    return get_reservations_by_service_by_date_range(
        start_date=start_date.strftime(date_format),
        end_date=end_date.strftime(date_format),
    )


def get_reservations_by_service_for_the_month() -> Reservations:
    end_date = datetime.now(tz=pytz.utc).date()
    start_date = end_date.replace(day=1)

    return get_reservations_by_service_by_date_range(
        start_date=start_date.strftime(date_format),
        end_date=end_date.strftime(date_format),
    )


def get_reservations_by_service_by_date_range(
    start_date: str, end_date: str
) -> Reservations:
    gingr = GingerRequests()

    return gingr.get_reservations_by_service(start_date=start_date, end_date=end_date)
