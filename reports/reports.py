from dataclasses import asdict, dataclass


@dataclass
class AccrualReport:
    start_date: str
    end_date: str
    requested_on: str
    revenue: float
    expenses: float
    net_profit: float
    margin: float
    number_reservations: int
    expense_report: str
    reservations_report: str
    id: None | int = None

    def to_dict(self):
        return asdict(self)
