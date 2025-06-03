class GlobalStats:
    """
    A class to hold global statistics for the application.
    This class is used to store and retrieve global statistics that can be accessed throughout the application.
    """

    # Global counters
    full_uptier_cnt_rt = 0
    full_downtier_cnt_rt = 0
    less_uptier_cnt_rt = 0
    less_downtier_cnt_rt = 0

    def __init__(self):
        self._stats = {}
