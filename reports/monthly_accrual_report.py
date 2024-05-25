from gingr.gingr_requests import GingerRequests


def main():
    gingr = GingerRequests()

    rev = gingr.get_pos_revenue(start_date="2024-05-19", end_date="2024-05-24")
    print(rev)
