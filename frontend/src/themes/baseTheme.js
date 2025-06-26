import { createTheme } from "@mui/material";

const baseTheme = createTheme({
    palette:{
        custom:{
            sidebar: "#424242",
            header: "#2E2E2E",
            main: "#666666",
            card: "#FFFFFF",
            sidebarText: "#FFFFFF",
            mintGreen: "#D1E8E2", 
            cardHeaderText:"#19747E", 
            cardHeaderBackgroundColor: "#A9D6E5", 
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

const cardTheme = {
    cardBasic: {
        width:"100%",
        height: "100%",
        borderRadius: "1em",
        boxShadow: "5px 5px 5px black;",
        display: "flex",
        justifyContent: "center"
    },
    cardHeader: {
        color: "custom.cardHeaderText",
        backgroundColor: "custom.cardHeaderBackgroundColor",
        fontWeight: "bold",
        fontSize: "1.25em",
        width: "100%",
        padding: "0.2em"
    },
    cardBody: {
        padding: "2em",
        textWrap: "pretty"
    }
}

export {baseTheme, cardTheme}