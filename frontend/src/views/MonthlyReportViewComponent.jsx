import { 
    Box, 
    Card, 
    CircularProgress, 
    Grid,
    Table,
    TableBody, 
    TableCell, 
    TableContainer, 
    TableHead, 
    TableRow, 
    Typography 
} from "@mui/material"
import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import { cardTheme } from "../themes/baseTheme"



const MonthlyReportViewComponent = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const year = searchParams.get("year");
    const month = searchParams.get("month");

    const [expenses, setExpenses] = useState();
    const [reservations, setReservations] = useState()
    const [highlights, setHighlights] = useState()

    const fetchMonthlyReprortData = async () => {
        const fetchURL = `http://localhost:5000/monthly-accrual-report/get-report?year=${year}&month=${month}`

        const resp = await fetch(fetchURL)
        const report = await resp.json()

        console.log(report)
        // parse data and generate the report data needed to view

        const date = new Date(report["start_date"])
        setHighlights({
            year: date.getFullYear(),
            month: date.getMonth() + 1,
            tot_reservations: +report["number_reservations"],
            tot_revenue: +report["revenue"].toFixed(2),
            tot_expenses: +report["expenses"].toFixed(2),
            net_profit: +report["net_profit"].toFixed(2),
            profit_margin: +report["margin"].toFixed(2)
        });
        setExpenses(JSON.parse(report["expense_report"]));
        setReservations(JSON.parse(report["reservations_report"]))


    }

    useEffect(() => {
        fetchMonthlyReprortData();
    }, [])
    const dataReady = highlights !== undefined && expenses !== undefined && reservations !== undefined;
    return(
        <Box
            display={"flex"}
            height={"100%"}
            width={"100%"}
        >
            {dataReady ?
                <Grid container spacing={2}>
                    <Grid item size={6} >
                        <Card sx={cardTheme.cardBasic}>
                            <TableContainer>
                                <Table sx={{ minWidth: 650, overflowY: "scroll" }}  size="small">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell sx={cardTheme.cardHeader} >
                                                {highlights.month > 9 ? highlights.month : `0${highlights.month}`} - {highlights.year}
                                            </TableCell>
                                            <TableCell sx={cardTheme.cardHeader} align="right">monthly value</TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>                                   
                                        <TableRow>
                                            <TableCell>Monthly Revenue</TableCell>
                                            <TableCell align="right">${highlights.tot_revenue.toFixed(2)}</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Number of Reservations</TableCell>
                                            <TableCell align="right">${highlights.tot_reservations}</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Monthly Expenses</TableCell>
                                            <TableCell align="right">${highlights.tot_expenses.toFixed(2)}</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Net Profit</TableCell>
                                            <TableCell align="right">${highlights.net_profit.toFixed(2)}</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell>Profit Margin</TableCell>
                                            <TableCell align="right">%{highlights.profit_margin.toFixed(2)}</TableCell>
                                        </TableRow>                    
                                    </TableBody>
                                </Table>
                            </TableContainer> 
                        </Card>    
                    </Grid>
                    <Grid item size={6}>
                        <Card sx={cardTheme.cardBasic}>
                            <TableContainer>
                                <Table sx={{ minWidth: 650, overflowY: "scroll" }}  size="small">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell sx={cardTheme.cardHeader} >
                                                Expenses
                                            </TableCell>
                                            <TableCell sx={cardTheme.cardHeader} align="right">
                                                total
                                            </TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {expenses.map((e, idx) => {

                                            return(
                                                <TableRow key={idx}>
                                                    <TableCell>
                                                        {e["title"]}
                                                    </TableCell>
                                                    <TableCell align="right">
                                                        {e["cost"].toFixed(2)}
                                                    </TableCell>
                                                </TableRow>
                                            )
                                        })}
                                    </TableBody>
                                </Table>
                            </TableContainer> 
                        </Card>    
                    </Grid>
                    <Grid 
                        item 
                        size={12}
                        sx={{
                            display: "flex",
                            justifyContent: "center",
                            width: "100%"
                        }}
                    >
                        <Card sx={cardTheme.cardBasic} >
                            <TableContainer>
                                <Table sx={{ minWidth: 650, overflowY: "scroll" }}  size="small">
                                    <TableHead>
                                        <TableRow>
                                            <TableCell sx={cardTheme.cardHeader} >
                                                Reservations
                                            </TableCell>
                                            <TableCell sx={cardTheme.cardHeader} align="right">
                                                number of reservations
                                            </TableCell>
                                            <TableCell sx={cardTheme.cardHeader} align="right">
                                                revenue total
                                            </TableCell>
                                        </TableRow>
                                    </TableHead>
                                    <TableBody>
                                        {Object.entries(reservations).map(([k, v]) => (
                                            <TableRow>
                                                <TableCell>
                                                    {k}
                                                </TableCell>
                                                <TableCell align="right">
                                                    {v.count}
                                                </TableCell>
                                                <TableCell align="right">
                                                    {v.revenue !== undefined ? v.revenue.toFixed(2): undefined}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer> 
                        </Card>    
                    </Grid>
                </Grid>
                : <CircularProgress />
            }
            
        </Box>
    );
}

export default MonthlyReportViewComponent;