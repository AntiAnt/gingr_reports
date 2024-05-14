from gingr.gingr_requests import GingerRequests


def main():
    gingr = GingerRequests()

    pos = gingr.get_pos_figures()

    print(pos)
