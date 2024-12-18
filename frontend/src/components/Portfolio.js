// frontend/src/components/Portfolio.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Table, Alert } from "react-bootstrap";

const Portfolio = () => {
  const [portfolio, setPortfolio] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        // Assuming there's an API endpoint to get portfolio data
        const token = localStorage.getItem("token"); // Adjust as per auth implementation
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/portfolio`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setPortfolio(response.data);
      } catch (err) {
        if (!err.response) {
          setError("Failed to fetch portfolio.");
        } else {
          // The API responded with some status code (like 400 or 500),
          // meaning we did connect, so do not set the error in this scenario
          console.error("API error:", err.response);
        }
      }
    };

    fetchPortfolio();
  }, []);

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  return (
    <Container style={{ marginTop: "50px" }}>
      <h2>Your Portfolio</h2>
      {portfolio.length === 0 ? (
        <p>No holdings found.</p>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Quantity</th>
              <th>Purchase Price</th>
              <th>Current Price</th>
              <th>Profit/Loss</th>
            </tr>
          </thead>
          <tbody>
            {portfolio.map((holding) => (
              <tr key={holding.ticker}>
                <td>{holding.ticker}</td>
                <td>{holding.quantity}</td>
                <td>${holding.purchase_price.toFixed(2)}</td>
                <td>${holding.current_price.toFixed(2)}</td>
                <td>
                  <span
                    style={{
                      color: holding.profit_loss >= 0 ? "green" : "red",
                    }}
                  >
                    ${holding.profit_loss.toFixed(2)}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
};

export default Portfolio;
