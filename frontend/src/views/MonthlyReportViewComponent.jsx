import { 
    Box, 
    Card, 
    Grid,
    Table,
    TableBody, 
    TableCell, 
    TableContainer, 
    TableHead, 
    TableRow, 
    Typography 
} from "@mui/material"
import { useState } from "react"

const theme = {
    cardBasic : {
        width:"100%",
        height: "100%",
        borderRadius: "1em",
        boxShadow: "5px 5px 5px black;",
        display: "flex",
        justifyContent: "center"
    },
    cardHeader : {
        color: "custom.cardHeaderText",
        backgroundColor: "custom.cardHeaderBackgroundColor",
        fontWeight: "bold",
        fontSize: "1.25em"
    }
}

const TEST_HIGHLIGHTS = {
    year: 2025,
    month: 5,
    tot_reservations: 347,
    tot_revenue: 13830.02345,
    tot_expenses: 14200.0003,
    net_profit: -369.97685,
    profit_margin: -2.6751715
}

const  TEST_EXPENSES = {
    "payroll": "$12,0000",
    "rent": "$2,200"
}

const TEST_RESERVATIONS = {
    "boarding": {numReservations: 35, revenueTotal: 2100},
    "fullday daycare": {numReservations: 300, revenueTotal: 10650},
    "puppy school": {numReservations: 12, revenueTotal: 1080},
}

const MonthlyReportViewComponent = () => {
    const [expenses, setExpenses] = useState(TEST_EXPENSES);
    const [reservations, setReservations] = useState(TEST_RESERVATIONS)
    const [highlights, setHighlights] = useState(TEST_HIGHLIGHTS)
    return(
        <Box
            display={"flex"}
            height={"100%"}
            width={"100%"}
        >
            <Grid container spacing={2}>
                <Grid item size={6} >
                    <Card sx={theme.cardBasic}>
                        <TableContainer>
                            <Table sx={{ minWidth: 650 }}  size="medium">
                                <TableHead>
                                    <TableRow>
                                        <TableCell sx={theme.cardHeader} >
                                            {highlights.month > 9 ? highlights.month : `0${highlights.month}`} - {highlights.year}
                                        </TableCell>
                                        <TableCell sx={theme.cardHeader} align="right">monthly value</TableCell>
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
                    <Card sx={theme.cardBasic}>
                        <TableContainer>
                            <Table sx={{ minWidth: 650 }}  size="medium">
                                <TableHead>
                                    <TableRow>
                                        <TableCell sx={theme.cardHeader} >
                                            Expenses
                                        </TableCell>
                                        <TableCell sx={theme.cardHeader} align="right">
                                            total
                                        </TableCell>
                                    </TableRow>
                                </TableHead>
                                <TableBody>
                                    {Object.entries(expenses).map(([k, v]) => (
                                        <TableRow>
                                            <TableCell>
                                                {k}
                                            </TableCell>
                                            <TableCell align="right">
                                                {v}
                                            </TableCell>
                                        </TableRow>
                                    ))}
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
                    <Card sx={theme.cardBasic} >
                        <TableContainer>
                            <Table sx={{ minWidth: 650 }}  size="small">
                                <TableHead>
                                    <TableRow>
                                        <TableCell sx={theme.cardHeader} >
                                            Reservations
                                        </TableCell>
                                        <TableCell sx={theme.cardHeader} align="right">
                                            number of reservations
                                        </TableCell>
                                         <TableCell sx={theme.cardHeader} align="right">
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
                                                {v.numReservations}
                                            </TableCell>
                                             <TableCell align="right">
                                                {v.revenueTotal}
                                            </TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </TableContainer> 
                    </Card>    
                </Grid>
            </Grid>
        </Box>
    );
}

export default MonthlyReportViewComponent;