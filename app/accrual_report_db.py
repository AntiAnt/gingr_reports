from abc import ABC, abstractmethod
from datetime import date
import sqlite3
from typing import Optional, Tuple

from reports.reports import AccrualReport




class AccrualReportDBManager(ABC):
    @abstractmethod
    def get_accrual_report_by_date_range(self, start_date: date, end_date: date) -> Optional[AccrualReport]:
        pass

    @abstractmethod
    def insert_report(self, report: AccrualReport) -> Optional[AccrualReport]:
        pass

    @abstractmethod
    def update_report(self, report: AccrualReport) -> Optional[int]:
        pass

    @abstractmethod
    def delete_report_by_id(self, id: int) -> Optional[int]:
        pass

    @abstractmethod
    def _create_new_report_from_row(self, row: Tuple) -> AccrualReport:
        pass


class SQLiteAccrualReportDBManager(AccrualReportDBManager):
    acruall_report_table_schema = """
            CREATE TABLE IF NOT EXISTS accrual_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                requested_on TEXT NOT NULL,
                revenue REAL NOT NULL,
                expenses REAL NOT NULL,
                net_profit REAL NOT NULL,
                margin REAL NOT NULL,
                UNIQUE(start_date, end_date)
            )
        """
    
    def __init__(self):
        self.database_name = "./accrual_reprot.db"
        conn = sqlite3.connect(self.database_name)

        conn.execute(self.acruall_report_table_schema)
        conn.commit()
        conn.close()

    def _create_new_report_from_row(self, row: Tuple) -> AccrualReport:
         return AccrualReport(
                id=row[0],
                start_date=row[1],
                end_date=row[2],
                requested_on=row[3],
                revenue=row[4],
                expenses=row[5],
                net_profit=row[6],
                margin=row[7]
            )


    def get_accrual_report_by_date_range(self, start_date: date, end_date: date) -> Optional[AccrualReport]:
        conn = sqlite3.connect(self.database_name)

        row = conn.execute(
            """
                SELECT * FROM accrual_reports WHERE start_date=? AND end_date=?;
            """,
            (start_date, end_date)
        ).fetchone()

        conn.close()

        if row is None:
            return
        
        return self._create_new_report_from_row(row)


    def insert_report(self, report: AccrualReport) -> Optional[AccrualReport]:
        conn = sqlite3.connect(self.database_name)

        cursor = conn.execute(
            """INSERT INTO accrual_reports
                (start_date, end_date, requested_on, revenue, expenses, net_profit, margin)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                report.start_date,
                report.end_date,
                report.requested_on,
                report.revenue,
                report.expenses,
                report.net_profit,
                report.margin
            )
        )

        conn.commit()
        conn.close()

        saved_report = self.get_accrual_report_by_date_range(start_date=report.start_date, end_date=report.end_date)

        if report is None:
            print(f"Accrual Report not saved. start data: {report.start_date}, end date: {report.end_date}")
            return
   
        print(f"Accrual Report saved. ID: {saved_report.id}")
        return saved_report
        

    def update_report(self, report: AccrualReport) -> Optional[int]:
        raise NotImplementedError()


    def delete_report_by_id(self, id: int) -> Optional[int]:
        raise NotImplementedError()


def get_accrual_reprot_record_manager():
    return SQLiteAccrualReportDBManager()