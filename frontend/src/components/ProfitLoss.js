// frontend/src/components/ProfitLoss.js
import React, { useState } from "react";
import { Form, Button, Container, Alert } from "react-bootstrap";
import axios from "axios";

const ProfitLoss = () => {
  const [ticker, setTicker] = useState("");
  const [pl, setPL] = useState(null);
  const [error, setError] = useState("");

  const handleFetchPL = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`/api/profit-loss?ticker=${ticker}`);
      setPL(response.data.profit_loss);
      setError("");
    } catch (err) {
      setError("Failed to fetch Profit/Loss.");
      setPL(null);
    }
  };

  return (
    <Container style={{ marginTop: "50px", maxWidth: "500px" }}>
      <h3>Calculate Profit/Loss</h3>
      <Form onSubmit={handleFetchPL}>
        <Form.Group controlId="formTicker" className="mb-3">
          <Form.Label>Stock/ETF Ticker</Form.Label>
          <Form.Control
            type="text"
            placeholder="Enter ticker"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            required
          />
        </Form.Group>
        <Button variant="primary" type="submit">
          Calculate
        </Button>
      </Form>
      {pl !== null && (
        <Alert variant={pl >= 0 ? "success" : "danger"} className="mt-3">
          Profit/Loss: ${pl.toFixed(2)}
        </Alert>
      )}
      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}
    </Container>
  );
};

export default ProfitLoss;
