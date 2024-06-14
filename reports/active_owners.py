from datetime import datetime, timedelta

import pytz

from gingr.gingr_reports import GingerReports, Owners


def get_active_owners_no_reservation_2_months() -> Owners:
    gingr = GingerReports()

    one_year_ago = datetime.now(tz=pytz.utc) - timedelta(days=365)
    two_months_ago = datetime.now(tz=pytz.utc) - timedelta(days=60)

    owners = gingr.get_owners()

    filtered_owners = []

    for owner in owners.owners:
        if owner.last_reservation is None:
            continue

        last_dt = datetime.strptime(owner.last_reservation, "%Y-%m-%d %H:%M:%S")
        localized_dt = pytz.utc.localize(last_dt)

        if one_year_ago < localized_dt < two_months_ago:
            filtered_owners.append(owner)

    return Owners(owners=filtered_owners)
