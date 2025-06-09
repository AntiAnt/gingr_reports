import { Box, Stack } from "@mui/material"


const AccrualReportComponent = (props) => {
    return(
        <Box>
            <Stack direction={"column"}>
                {Object.entries(props.report).map(([k, v]) => (
                    <Box>
                        <dt>{k}</dt>
                        <dd>{v}</dd>
                    </Box>
                    
                ))}
            </Stack>
        </Box>
    );
}

export default AccrualReportComponent;