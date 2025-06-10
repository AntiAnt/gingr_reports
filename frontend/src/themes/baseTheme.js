import { createTheme } from "@mui/material";

const baseTheme = createTheme({
    palette:{
        custom:{
            sidebar: "#424242",
            header: "#2E2E2E",
            main: "#666666",
            card: "#FFFFFF",
            sidebarText: "#FFFFFF"
        }
    },
    typography: {
        h4: {
            fontWeight: 700,
            color: "#FFFFFF",
        },
        h6: {
            fontWeight: 600,
            color: "#333",
        },
        body1: {
            color: "#555",
        },
    },
})

export {baseTheme}