import { Card, Typography } from '@mui/material';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';
import Box from '@mui/material/Box';
import { cardTheme } from '../themes/baseTheme';
import { useState } from 'react';

const currentYear = dayjs();

const DashboardViewComponent = () => {
    const [monthlyAccrualDateSelection, setMonthlyAccrualDateSelection] = useState();

    const handleDateChange = (e) => {
        setMonthlyAccrualDateSelection({
            year: e.year(),
            month: e.month() + 1 // month is zero indexed
        })
    }

    return(
        <Box
            sx={{display: "flex", height: "100%", width: "100%", border: "solid gold"}}
        >
            <Card sx={{
                    width: "100%",
                    flexDirection:"column",
                    ...cardTheme.cardBasic
                }}
            >
                <Box sx={cardTheme.cardHeader}>
                    <Typography variant='h4'>Monthly Accrual Reprot</Typography>
                </Box>
                <Box>
                    <LocalizationProvider dateAdapter={AdapterDayjs}>
                        <DatePicker
                            label="Years in descending order"
                            maxDate={currentYear}
                            onChange={handleDateChange}
                            openTo="year"
                            views={['year', 'month']}
                            yearsOrder="desc"
                            sx={{ minWidth: 250 }}
                        />
                    </LocalizationProvider>
                </Box>
            </Card>
        

        </Box>
    )
}

export default DashboardViewComponent;