// Chart.js
import React, { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import axios from "axios";
import { Spinner } from "react-bootstrap";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const HistoricalChart = ({ ticker }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchHistorical = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_API_URL}/historical?ticker=${ticker}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        const { dates, prices } = response.data;
        setData({
          labels: dates,
          datasets: [
            {
              label: `${ticker} Historical Prices`,
              data: prices,
              borderColor: "#00c853",
              backgroundColor: "rgba(0, 200, 83, 0.2)",
            },
          ],
        });
      } catch (err) {
        console.error("Failed to fetch historical data", err);
      }
    };
    if (ticker) {
      fetchHistorical();
    }
  }, [ticker]);

  if (!data) return <Spinner animation="border" />;

  return (
    <div
      style={{
        backgroundColor: "#1e1e1e",
        padding: "20px",
        borderRadius: "8px",
        marginTop: "20px",
      }}
    >
      <h5 style={{ color: "#ffffff", marginBottom: "20px" }}>
        {ticker} Historical Chart
      </h5>
      <Line
        data={data}
        options={{ responsive: true, plugins: { legend: { display: false } } }}
      />
    </div>
  );
};

export default HistoricalChart;
