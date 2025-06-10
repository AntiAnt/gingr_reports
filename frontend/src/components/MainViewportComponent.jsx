import { Box } from "@mui/material";
import AccrualReportComponent from "./AccrualReportComponent";
import { useEffect, useState } from "react";

const DEFAULT_REPORT = {
    revenue: 100.0,
    expenses: 80.0,
    net_profit: 20.0,
    margin: 20.0,
}

const MainViewportComponent = (props) => {
    const [report, setReport] = useState(DEFAULT_REPORT);
    const [searchStartDate, setSearchStartDate] = useState("2025-04-01");
    const [searchEndDate, setSearchEndDate] = useState("2025-04-30")

    const fetchAccrualData = async () => {
         try {
            const formData = new FormData();
            formData.append("start-date", searchStartDate);
            formData.append("end-date", searchEndDate);

            const response = await fetch(
                "http://localhost:5000/monthly-accrual-report/get-report", {
                    method: "POST",
                    body: formData
                }
            );

            if (!response.ok) {
                throw new Error(`failed to fetch reports. params: ${formData}`)
            }
            const data = await response.json()
            setReport(data)
        } catch (err){
            console.error("fetch error:", err.message)
        }
    }

    // useEffect(() => {
    //    fetchAccrualData();
    // }, [])
    return(
        <Box sx={{border: "solid", borderColor: "gold"}}>
            <AccrualReportComponent report={report}/>
        </Box>
    )
}

export default MainViewportComponent;