// frontend/src/components/Dashboard.js

import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  Container,
  Form,
  Button,
  Alert,
  Spinner,
  Tabs,
  Tab,
} from "react-bootstrap";
import StrategyList from "./StrategyList";
import io from "socket.io-client";

const Dashboard = () => {
  const [tickers, setTickers] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [predictions, setPredictions] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    // Initialize WebSocket connection
    const newSocket = io(
      `${process.env.REACT_APP_API_URL.replace(/^http/, "ws")}/ws`
    );
    setSocket(newSocket);
    return () => newSocket.close();
  }, [setSocket]);

  useEffect(() => {
    if (socket) {
      socket.on("message", (data) => {
        const message = JSON.parse(data);
        const { ticker, predicted_close, recommended_strategies } = message;
        setPredictions((prev) => ({
          ...prev,
          [ticker]: {
            predicted_close,
            recommended_strategies,
          },
        }));
      });
    }
  }, [socket]);

  const handleAddTicker = () => {
    const ticker = selectedTicker.trim().toUpperCase();
    if (ticker && !tickers.includes(ticker)) {
      setTickers([...tickers, ticker]);
      setSelectedTicker("");
      fetchPrediction(ticker);
    }
  };

  const fetchPrediction = async (ticker) => {
    try {
      setLoading(true);
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL}/predict`,
        {
          ticker,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }
      );
      setPredictions((prev) => ({
        ...prev,
        [ticker]: response.data,
      }));
      setLoading(false);
    } catch (err) {
      setPredictions((prev) => ({
        ...prev,
        [ticker]: {
          error: err.response ? err.response.data.detail : "Server Error",
        },
      }));
      setLoading(false);
    }
  };

  return (
    <Container style={{ marginTop: "50px" }}>
      <h2>Options Trading Dashboard</h2>

      <Form className="d-flex mt-4">
        <Form.Control
          type="text"
          placeholder="Enter Ticker Symbol (e.g., AAPL)"
          value={selectedTicker}
          onChange={(e) => setSelectedTicker(e.target.value)}
        />
        <Button variant="primary" className="ms-2" onClick={handleAddTicker}>
          Add
        </Button>
      </Form>

      {loading && <Spinner animation="border" className="mt-3" />}

      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}

      {tickers.length > 0 ? (
        <Tabs
          defaultActiveKey={tickers[0]}
          id="stock-tabs"
          className="mt-4"
          fill
        >
          {tickers.map((ticker) => (
            <Tab eventKey={ticker} title={ticker} key={ticker}>
              <div className="mt-3">
                {predictions[ticker] ? (
                  predictions[ticker].error ? (
                    <Alert variant="danger">{predictions[ticker].error}</Alert>
                  ) : (
                    <>
                      <h4>
                        Predicted Close Price: $
                        {predictions[ticker].predicted_close}
                      </h4>
                      <h5>Recommended Strategies:</h5>
                      <StrategyList
                        strategies={predictions[ticker].recommended_strategies}
                      />
                      {/* Placeholder for charts or additional data */}
                      {/* Implement charts as needed */}
                    </>
                  )
                ) : (
                  <Spinner animation="border" />
                )}
              </div>
            </Tab>
          ))}
        </Tabs>
      ) : (
        <p className="mt-4">
          No tickers added yet. Please add a ticker to view predictions and
          strategies.
        </p>
      )}
    </Container>
  );
};

export default Dashboard;
