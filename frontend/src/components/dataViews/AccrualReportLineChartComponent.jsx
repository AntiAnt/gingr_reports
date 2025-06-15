import {BarChart} from '@mui/x-charts';



const AccrualReportLineChartComponent = ({series, dataKey }) => {
    return(
        <BarChart
            dataset={series}
            xAxis={[{ scaleType: 'band', dataKey: 'month' }]}
            series={[{ dataKey: dataKey, label: dataKey }]}
            height={400}
        />
    )
}



export default AccrualReportLineChartComponent;