import { Box, Paper } from "@mui/material"

import AccrualReportLineChartComponent from "./dataViews/AccrualReportLineChartComponent";

const AccrualChartGroupComponent = ({reportSeries}) => {
    return(
        <Box sx={{bgcolr: "custom.main"}}>
            <Paper
                elevation={3}
                sx={{
                    p: 2,
                    bgcolor: "custom.card",
                    borderRadius: 1,
                    textAlign: "center",
                }}
            >
                <AccrualReportLineChartComponent series={reportSeries} dataKey="revenue"/>
            </Paper>
            <Paper
                elevation={3}
                sx={{
                    p: 2,
                    bgcolor: "custom.card",
                    borderRadius: 1,
                    textAlign: "center",
                }}
            >
                <AccrualReportLineChartComponent series={reportSeries} dataKey="expenses"/>
            </Paper>
            <Paper
                elevation={3}
                sx={{
                    p: 2,
                    bgcolor: "custom.card",
                    borderRadius: 1,
                    textAlign: "center",
                }}
            >
                    <AccrualReportLineChartComponent series={reportSeries} dataKey="net_profit"/>
            </Paper>
            <Paper
                elevation={3}
                sx={{
                    p: 2,
                    bgcolor: "custom.card",
                    borderRadius: 1,
                    textAlign: "center",
                }}
            >
                <AccrualReportLineChartComponent series={reportSeries} dataKey="margin"/>
            </Paper>
            
        </Box>
    )
}

export default AccrualChartGroupComponent;