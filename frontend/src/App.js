import SidebarComponent from "./components/SidebarComponent";
import HeaderComponent from "./components/HeaderComponent";
import MainViewportComponent from "./components/MainViewportComponent";
import { Grid } from "@mui/material";
import { Router } from "react-router-dom";

function App() {
  return (
        <Grid container spacing={2}>
          <Grid size={12}>
            <HeaderComponent/>
          </Grid>
          <Grid size={2}>
            <SidebarComponent/>
          </Grid>
          <Grid size={10}>
            <MainViewportComponent />
          </Grid>
        </Grid>
  );
}

export default App;
