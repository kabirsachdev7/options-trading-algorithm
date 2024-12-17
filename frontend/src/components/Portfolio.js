import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Form, Button, Table, Alert } from "react-bootstrap";
import CurrentPrice from "./CurrentPrice";
import ProfitLoss from "./ProfitLoss";

const Portfolio = () => {
  const [holdings, setHoldings] = useState([]);
  const [ticker, setTicker] = useState("");
  const [quantity, setQuantity] = useState("");
  const [purchasePrice, setPurchasePrice] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const userId = parseInt(localStorage.getItem("user_id")); // Replace with actual user ID retrieval

  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/portfolio/${userId}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      setHoldings(response.data.holdings);
    } catch (err) {
      setError("Failed to fetch portfolio.");
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handleAddHolding = async (e) => {
    e.preventDefault();
    try {
      const newHolding = {
        ticker: ticker.toUpperCase(),
        quantity: parseInt(quantity),
        purchase_price: parseFloat(purchasePrice),
      };
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/portfolio/${userId}/holdings`,
        newHolding,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      setHoldings([...holdings, response.data]);
      setTicker("");
      setQuantity("");
      setPurchasePrice("");
      setSuccess("Holding added successfully.");
    } catch (err) {
      setError("Failed to add holding.");
    }
  };

  return (
    <Container className="mt-5">
      <h3>Your Portfolio</h3>
      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}
      <Form onSubmit={handleAddHolding} className="mt-3">
        <Form.Group controlId="ticker">
          <Form.Label>Ticker Symbol</Form.Label>
          <Form.Control
            type="text"
            placeholder="Enter ticker"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            required
          />
        </Form.Group>

        <Form.Group controlId="quantity" className="mt-3">
          <Form.Label>Quantity</Form.Label>
          <Form.Control
            type="number"
            placeholder="Enter quantity"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            required
          />
        </Form.Group>

        <Form.Group controlId="purchasePrice" className="mt-3">
          <Form.Label>Purchase Price</Form.Label>
          <Form.Control
            type="number"
            step="0.01"
            placeholder="Enter purchase price"
            value={purchasePrice}
            onChange={(e) => setPurchasePrice(e.target.value)}
            required
          />
        </Form.Group>

        <Button variant="primary" type="submit" className="mt-4">
          Add Holding
        </Button>
      </Form>

      <Table striped bordered hover className="mt-5">
        <thead>
          <tr>
            <th>#</th>
            <th>Ticker</th>
            <th>Quantity</th>
            <th>Purchase Price</th>
            <th>Current Price</th>
            <th>Profit/Loss</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding, index) => (
            <tr key={holding.id}>
              <td>{index + 1}</td>
              <td>{holding.ticker}</td>
              <td>{holding.quantity}</td>
              <td>${holding.purchase_price}</td>
              <td>
                <CurrentPrice ticker={holding.ticker} />
              </td>
              <td>
                <ProfitLoss holding={holding} />
              </td>
            </tr>
          ))}
        </tbody>
      </Table>
    </Container>
  );
};

export default Portfolio;
