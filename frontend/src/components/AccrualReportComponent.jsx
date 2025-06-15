import { Box, CircularProgress, Paper } from "@mui/material"
import { useEffect, useMemo, useState } from "react"

import AccrualReportChartGroupComponent from "./AccrualChartGroupComponent";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"];

const AccrualReportComponent = () => {
    const [reports, setReports] = useState();

    const fetchMontlyAccrualData = async () => {
        try {
            const response = await fetch(
                "http://localhost:5000/monthly-accrual-report/ytd",
                {
                    method: "GET"
                }
            );

            const data = await response.json();
            setReports(data);
        } catch (error) {
            console.error(error);
        }
    };

    const conformReports = (reports) => {
        if (reports === undefined || Object.keys(reports).length === 0) {
            return Array.from({length: 12}, (_, idx) => ({
                revenue: 0,
                expenses: 0,
                net_profit: 0,
                margin: 0,
                month: MONTHS[idx]
            }));
        }

        return Array.from({length: 12}, (_,idx) =>{
            const report = reports[idx + 1] || {
                revenue: 0,
                expenses: 0,
                net_profit: 0,
                margin: 0,
            }
            return {...report, month: MONTHS[idx]}

        });
    };

    useEffect(() => {
        fetchMontlyAccrualData();
    }, []);

    const conformedReports = useMemo(() => (conformReports(reports)), [reports])

    return(
        <Box>
            {reports === undefined ?
                <CircularProgress /> :
                <AccrualReportChartGroupComponent reportSeries={conformedReports}/>
            }
        </Box>
    );
}

export default AccrualReportComponent;