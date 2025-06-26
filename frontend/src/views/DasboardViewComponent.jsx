import { Button, ButtonGroup, Card, Grid, Typography } from '@mui/material';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import dayjs from 'dayjs';
import Box from '@mui/material/Box';
import { cardTheme } from '../themes/baseTheme';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const currentYear = dayjs();

const DashboardViewComponent = () => {
    const navigate = useNavigate()
    const [monthlyAccrualDateSelection, setMonthlyAccrualDateSelection] = useState();
    console.log(monthlyAccrualDateSelection)
    const validYearMonth = (dateObj) => {
        console.log(dateObj)
        return dateObj !== undefined && dateObj.year !== undefined && dateObj.month !== undefined;
    }
    const handleDateChange = (e) => {
        console.log("FIRED")
        setMonthlyAccrualDateSelection({
            year: e.year(),
            month: e.month() + 1 // month is zero indexed
        })
    }

    const handleMonthlyAccrualDateSelectionClick = () => {
        if (validYearMonth(monthlyAccrualDateSelection)) {
            const navPath = `/monthly-accrual-report/get-report?year=${monthlyAccrualDateSelection.year}&month=${monthlyAccrualDateSelection.month}`
            navigate(navPath)
        }
    }

    return(
        <Box
            sx={{display: "flex", height: "100%", width: "100%"}}
        >
            <Grid sx={{width: "100%"}}container spacing={2}>
                <Grid item size={12} sx={{display: "flex", justifyContent: "center"}}>
                     <Card sx={{
                            width: "100%",
                            flexDirection:"column",
                            position: 'relative',
                            justifyContent: "center",
                            ...cardTheme.cardBasic
                        }}
                    >
                        <Box sx={{
                            position: "absolute",
                            top: 0,
                            left: 0,
                            width: "100%"
                        }}>
                             <Box sx={{

                                ...cardTheme.cardHeader
                            }}>
                                <Typography variant='h4'>Monthly Accrual Reprot</Typography>
                            </Box>
                            <Box
                                sx={{
                                    padding: "1em"
                                }}
                            >
                                <Typography variant='body1' sx={cardTheme.cardBody}>
                                    This is a placeholder for very important text about this feature. More to come!
                                </Typography>
                                <ButtonGroup fullWidth >
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
                                    <Button 
                                        variant="text" 
                                        onClick={handleMonthlyAccrualDateSelectionClick}
                                        disabled={!validYearMonth(monthlyAccrualDateSelection)}
                                    >
                                        Get Report
                                    </Button>
                                </ButtonGroup>
                                
                            </Box>
                        </Box>
                       
                    </Card>
                </Grid>
                <Grid size={12}>
                    <Card sx={{
                            width: "100%",
                            flexDirection:"column",
                            ...cardTheme.cardBasic
                        }}
                    >
                    </Card>
                </Grid>

                
            </Grid>
            
        </Box>
    )
}

export default DashboardViewComponent;