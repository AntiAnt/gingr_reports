import calendar
import os
import pdb
from dataclasses import asdict
from datetime import date

from flask import Flask, jsonify, redirect, request, url_for
from flask_cors import CORS
from intuitlib.client import AuthClient
from intuitlib.enums import Scopes

from constants import (INTUIT_CLIENT_ID, INTUIT_CLIENT_SECRET,
                       MONTHLY_ACCRUAL_REDIRECT_URI)
from reports.active_owners import get_active_owners_no_reservation_2_months
from reports.monthly_accrual_report import (
    AccrualReport, generate_ytd_historic_monthly_accrual_reports,
    get_monthly_acrual_report, get_ytd_historic_monthly_accrual_reports)
from reports.reservations import (get_reservations_by_service_by_date_range,
                                  get_reservations_by_service_for_the_month,
                                  get_reservations_by_service_for_the_week)

from .auth_db_manager import SessionTokens, get_auth_manager

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

intuit_auth_manager = get_auth_manager()


@app.route("/")
def root():
    return """
        <div>
            <h1>Home</h1>
            <button onclick=window.location.href="/dashboard">- Dashboard -</button> 
        </div>
    """


@app.route("/dashboard")
def dashboard():
    session_tokens: SessionTokens | None = (
        intuit_auth_manager.get_latest_session_tokens()
    )
    if session_tokens is None:
        return redirect(url_for("qb_login"))

    if session_tokens.is_access_token_expired():
        if session_tokens.is_refresh_token_expired():
            return redirect(url_for("qb_login"))
        else:
            auth_client = AuthClient(
                client_id=os.getenv(INTUIT_CLIENT_ID),
                client_secret=os.getenv(INTUIT_CLIENT_SECRET),
                access_token=session_tokens.access_token,
                refresh_token=session_tokens.refresh_token,
                realm_id=session_tokens.realm_id,
                environment="sandbox",
                redirect_uri=MONTHLY_ACCRUAL_REDIRECT_URI,
            )

            auth_client.refresh()

            assert auth_client.access_token != session_tokens.access_token

            intuit_auth_manager.update_session_tokens_access_token(
                id=session_tokens.id, access_token=auth_client.access_token
            )

    return """
            <div>
                <h1>Dashboard</h1>
                <div>
                    <h2>Monthly Accrual Report</h2>
                    <form action="/monthly-accrual-report/get-report" method="post">
                        Start Date: <input type="date" name="start_date"><br>
                        End Date: <input type="date" name="end_date"><br>
                        <input type="submit" value="Generate Report">
                    </form>
                </div>
                <div>
                    <h2>Reservations by Service</h2>
                    <button onclick=window.location.href="/reservations-by-service/week">Current Week</button>
                    <h4>OR</h4>
                    <button onclick=window.location.href="/reservations-by-service/month">Current Month</button>
                    <h4>OR</h4>
                    <form action="/reservations-by-service/date_range" method="post">
                        Start Date: <input type="date" name="start-date"><br>
                        End Date: <input type="date" name="end-date"><br>
                        <input type="submit" value="Custom date range(30 day limit)">
                    </form>
                </div>
                <div>
                    <h2>Active Owners With No Recent Reservations</h2>
                    <button onclick=window.location.href="/active-owners/no-recent-reservations">Get Owners</button>
                </div>
            <div>
        """


@app.route("/monthly-accrual-report/auth")
def qb_login():
    auth_client = AuthClient(
        client_id=os.getenv(INTUIT_CLIENT_ID),
        client_secret=os.getenv(INTUIT_CLIENT_SECRET),
        environment="sandbox",
        redirect_uri=MONTHLY_ACCRUAL_REDIRECT_URI,
    )
    auth_url = auth_client.get_authorization_url(scopes=[Scopes.ACCOUNTING])
    print(f"AUTH URL {auth_url}")
    return redirect(auth_url)


@app.route("/monthly-accrual-report/auth_callback")
def qb_auth_callback():
    auth_code = request.args.get("code")
    realm_id = request.args.get("realmId")
    auth_client = AuthClient(
        client_id=os.getenv(INTUIT_CLIENT_ID),
        client_secret=os.getenv(INTUIT_CLIENT_SECRET),
        environment="sandbox",
        redirect_uri=MONTHLY_ACCRUAL_REDIRECT_URI,
    )
    # get access and refresh token
    auth_client.get_bearer_token(auth_code=auth_code, realm_id=realm_id)

    intuit_auth_manager.put_session_tokens(
        access_token=auth_client.access_token,
        refresh_token=auth_client.refresh_token,
        realm_id=int(auth_client.realm_id),
    )

    return redirect("/")


@app.route("/monthly-accrual-report/get-report", methods=["get"])
def get_monthly_accrual():
    year = int(request.args.get("year"))
    month = int(request.args.get("month"))

    start_date_iso_str = date(year=year, month=month, day=1).isoformat()
    end_date_iso_str = date(
        year=year, month=month, day=calendar.monthrange(year=year, month=month)[-1]
    ).isoformat()

    latest_session_token = intuit_auth_manager.get_latest_session_tokens()

    auth_client = AuthClient(
        client_id=os.getenv(INTUIT_CLIENT_ID),
        client_secret=os.getenv(INTUIT_CLIENT_SECRET),
        access_token=latest_session_token.access_token,
        refresh_token=latest_session_token.refresh_token,
        realm_id=latest_session_token.realm_id,
        environment="sandbox",
        redirect_uri=MONTHLY_ACCRUAL_REDIRECT_URI,
    )

    report: AccrualReport = get_monthly_acrual_report(
        intuit_auth_client=auth_client, start_date=start_date_iso_str, end_date=end_date_iso_str
    )
    return jsonify(asdict(report))


@app.route("/monthly-accrual-report/ytd", methods=["get"])
def get_ytd_monthly_accrual_reports():
    today = date.today()
    past_reports = get_ytd_historic_monthly_accrual_reports(today.year)

    latest_session_token = intuit_auth_manager.get_latest_session_tokens()

    auth_client = AuthClient(
        client_id=os.getenv(INTUIT_CLIENT_ID),
        client_secret=os.getenv(INTUIT_CLIENT_SECRET),
        access_token=latest_session_token.access_token,
        refresh_token=latest_session_token.refresh_token,
        realm_id=latest_session_token.realm_id,
        environment="sandbox",
        redirect_uri=MONTHLY_ACCRUAL_REDIRECT_URI,
    )

    if len(past_reports) < today.month - 1:
        generated_past_reports = generate_ytd_historic_monthly_accrual_reports(
            year=today.year,
            monthly_accrual_reports=past_reports,
            intuit_auth_client=auth_client,
            range_month_end=today.month - 1,
        )
        return jsonify(generated_past_reports | past_reports)

    # current_month_report = generate_current_month_accrual_reprort(
    #     current_date=today, intuit_auth_client=auth_client
    # )

    return jsonify(past_reports)


@app.route("/monthly-accrual-report/ytd/historic", methods=["post"])
def get_ytd_monthly_accrual_reports_by_year():
    year = int(request.form["year"])
    if year == date.today().year:
        return get_ytd_monthly_accrual_reports()

    reports = get_ytd_historic_monthly_accrual_reports(year)

    if len(reports) != 12:
        latest_session_token = intuit_auth_manager.get_latest_session_tokens()

        auth_client = AuthClient(
            client_id=os.getenv(INTUIT_CLIENT_ID),
            client_secret=os.getenv(INTUIT_CLIENT_SECRET),
            access_token=latest_session_token.access_token,
            refresh_token=latest_session_token.refresh_token,
            realm_id=latest_session_token.realm_id,
            environment="sandbox",
            redirect_uri=MONTHLY_ACCRUAL_REDIRECT_URI,
        )

        return jsonify(
            generate_ytd_historic_monthly_accrual_reports(
                year=year,
                monthly_accrual_reports=reports,
                intuit_auth_client=auth_client,
            )
        )

    return jsonify(reports)


@app.route("/reservations-by-service/week", methods={"get"})
def reservations_by_service_for_the_week():
    return jsonify(get_reservations_by_service_for_the_week())


@app.route("/reservations-by-service/month", methods={"get"})
def reservations_by_service_for_the_month():
    return jsonify(get_reservations_by_service_for_the_month())


@app.route("/reservations-by-service/date_range", methods={"post"})
def reservations_by_service_by_date_range():
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    return jsonify(
        get_reservations_by_service_by_date_range(
            start_date=start_date, end_date=end_date
        )
    )


@app.route("/active-owners/no-recent-reservations")
def get_active_owners_no_recent_reservations():
    return jsonify(get_active_owners_no_reservation_2_months())


def main():
    # TODO:  add check for api keys and tokens
    # TODO: read api keys from config file

    app.run(host="0.0.0.0", debug=True, port=5000)
