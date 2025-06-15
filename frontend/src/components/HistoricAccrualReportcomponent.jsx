import { Box, Button, TextField } from "@mui/material";
import { useMemo, useState } from "react";
import AccrualChartGroupComponent from "./AccrualChartGroupComponent";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sept", "Oct", "Nov", "Dec"];


const HistoricAccrualReportcomponent = () => {
    const [year, setYear] = useState("");
    const [reports, setReports] = useState(undefined)

    const updateYearInput = (year) => {
        setYear(+year)
    }

    const fetchHistoricYtdData = async (year) => {
        try {
             const formData = new FormData();
                formData.append("year", year);
            const response = await fetch(`http://localhost:5000/monthly-accrual-report/ytd/historic`, {
                
                method: "POST",
                body: formData
            });
        const data = await response.json();
            setReports(data);
        } catch (error) {
            console.error(`Error fetching historic YTD data for ${year}:`, error);
        }
    };

    const handleFetch = () => {
        if (!isNaN(year) && year >= 2000 && year <= 2100) { // Basic validation
            fetchHistoricYtdData(year);
        } else {
            alert('Please enter a valid year between 2000 and 2100');
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

    const conformedReports = useMemo(() => (conformReports(reports)))

    return(
        <Box>
            <TextField 
                label="Enter Year"
                value={year}
                onChange={(e) => updateYearInput(e.target.value)}
                variant="outlined"
                sx={{ width: 150 }}
            />
            <Button
                variant="contained"
                onClick={handleFetch}
            >
                Fetch
            </Button>
            <AccrualChartGroupComponent reportSeries={conformedReports} />
        </Box>
    )
}

export default HistoricAccrualReportcomponent;