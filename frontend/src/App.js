import { Box, ThemeProvider, Typography } from "@mui/material";
import { baseTheme } from "./themes/baseTheme";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainViewportComponent from "./components/MainViewportComponent";
import AccrualReportComponent from "./components/AccrualReportComponent";
import HistoricAccrualReportcomponent from "./components/HistoricAccrualReportcomponent";
import MonthlyReportViewComponent from "./views/MonthlyReportViewComponent";
import DashboardViewComponent from "./views/DasboardViewComponent";

function App() {
  const categories = ["Monthly Accrual", "Upload"];

  return (
    <ThemeProvider theme={baseTheme}>
      <Box sx={{ display: "flex", height: "100vh", overflow: "hidden" }}>
        <Box
          sx={{
            width: 250,
            bgcolor: "custom.sidebar",
            color: "#FFFFFF",
            padding: (theme) => theme.spacing(2),
          }}
        >
          <Typography variant="h6">Categories</Typography>
          {categories.map((category, index) => (
            <Typography key={index} sx={{ mt: 1 }}>
              {category}
            </Typography>
          ))}
        </Box>
        <Box sx={{ flex: 1, display: "flex", flexDirection: "column", bgcolor: "custom.main" }}>
          <Box
            sx={{
              bgcolor: "custom.header",
              color: "#FFFFFF",
              padding: (theme) => theme.spacing(2),
              textAlign: "center",
            }}
          >
            <Typography variant="h4">Accrual Reports</Typography>
          </Box>
          <Box
            sx={{
              flex: 1,
              minHeight: 0,
              p: 3,
              overflowY: "auto",
              display: "flex",
              flexDirection: "column",
              gap: 2,
            }}
          >
            <Router>
              <Routes>
                <Route path="/" element={<DashboardViewComponent />}>
                  <Route path="/ytd-monthly-accrual" element={<AccrualReportComponent />}/>
                </Route>
                <Route path="/historic/ytd-monthly-accrual" element={<HistoricAccrualReportcomponent />}/>
                <Route path="/monthly-report" element={<MonthlyReportViewComponent />} />
                <Route path="/monthly-accrual-report/get-report" element={<MonthlyReportViewComponent />} />
              </Routes>
            </Router>
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
