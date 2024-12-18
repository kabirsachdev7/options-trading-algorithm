// Portfolio.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Table, Alert, Card } from "react-bootstrap";

const Portfolio = () => {
  const [portfolio, setPortfolio] = useState([]);
  const [error, setError] = useState("");
  const [totalValue, setTotalValue] = useState(0);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          `${process.env.REACT_APP_API_URL}/portfolio`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setPortfolio(response.data);

        const value = response.data.reduce(
          (acc, h) => acc + h.current_price * h.quantity,
          0
        );
        setTotalValue(value);
      } catch (err) {
        setError("Failed to fetch portfolio.");
      }
    };

    fetchPortfolio();
  }, []);

  if (error) {
    return (
      <Alert variant="danger" className="mt-4">
        {error}
      </Alert>
    );
  }

  return (
    <Container style={{ marginTop: "50px" }}>
      <h2>Your Portfolio</h2>
      <p className="text-muted">
        Total Portfolio Value:{" "}
        <span style={{ color: "#00c853" }}>${totalValue.toFixed(2)}</span>
      </p>
      {portfolio.length === 0 ? (
        <p>No holdings found.</p>
      ) : (
        <Card
          style={{
            backgroundColor: "#1e1e1e",
            borderRadius: "8px",
            padding: "20px",
          }}
        >
          <Table striped bordered hover className="mt-3">
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
                        color: holding.profit_loss >= 0 ? "#00c853" : "#ff5252",
                      }}
                    >
                      ${holding.profit_loss.toFixed(2)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      )}
    </Container>
  );
};

export default Portfolio;
