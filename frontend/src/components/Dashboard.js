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
  Card,
  Row,
  Col,
  Table,
} from "react-bootstrap";
import StrategyList from "./StrategyList";
import HistoricalChart from "./Chart";

const Dashboard = () => {
  const [tickers, setTickers] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [predictions, setPredictions] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [watchlist, setWatchlist] = useState(["AAPL", "TSLA"]);

  // Separate state for the watchlist input
  const [watchlistTicker, setWatchlistTicker] = useState("");

  const [tradeTicker, setTradeTicker] = useState("");
  const [tradeAction, setTradeAction] = useState("BUY");
  const [tradeQuantity, setTradeQuantity] = useState(0);

  useEffect(() => {
    const wsUrl = `${process.env.REACT_APP_API_URL.replace(/^http/, "ws")}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        const { ticker, predicted_close, recommended_strategies } = message;
        setPredictions((prev) => ({
          ...prev,
          [ticker]: { predicted_close, recommended_strategies },
        }));
      } catch (err) {
        console.error("Error parsing WebSocket message:", err);
      }
    };

    ws.onerror = (errorEvent) => console.error("WebSocket error:", errorEvent);
    ws.onclose = () => console.log("WebSocket closed.");

    return () => ws.close();
  }, []);

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
        { ticker },
        {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        }
      );
      setPredictions((prev) => ({ ...prev, [ticker]: response.data }));
      setLoading(false);
    } catch (err) {
      setPredictions((prev) => ({
        ...prev,
        [ticker]: {
          error: err.response ? err.response.data.detail : "Server Error",
        },
      }));
      setError(
        "Failed to fetch prediction. " +
          (err.response ? err.response.data.detail : "")
      );
      setLoading(false);
    }
  };

  const addToWatchlist = (t) => {
    if (t && !watchlist.includes(t)) setWatchlist([...watchlist, t]);
  };

  const removeFromWatchlist = (t) => {
    setWatchlist(watchlist.filter((item) => item !== t));
  };

  const handleTrade = (e) => {
    e.preventDefault();
    alert(
      `Executed ${tradeAction} of ${tradeQuantity} shares of ${tradeTicker}`
    );
    setTradeTicker("");
    setTradeQuantity(0);
  };

  return (
    <Container fluid style={{ marginLeft: "220px", paddingTop: "30px" }}>
      <h2 className="mb-4" style={{ color: "#ffffff" }}>
        Options Trading Dashboard
      </h2>

      {/* Quick Actions */}
      <Card className="mb-4">
        <Card.Body>
          <h4>Quick Actions</h4>
          <Form className="d-flex mt-3 mb-3">
            <Form.Control
              type="text"
              placeholder="Enter Ticker Symbol"
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
              style={{ color: "#ffffff" }}
            />
            <Button
              variant="primary"
              className="ms-2"
              onClick={handleAddTicker}
            >
              Add
            </Button>
          </Form>
          <Button
            variant="outline-light"
            className="me-2"
            onClick={() => tickers.forEach((t) => fetchPrediction(t))}
          >
            Refresh All
          </Button>
          <Button
            variant="outline-light"
            onClick={() => (window.location.href = "/portfolio")}
          >
            View Portfolio
          </Button>
        </Card.Body>
      </Card>

      {loading && <Spinner animation="border" className="mt-3" />}

      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}

      <Row>
        <Col md={4}>
          {/* Market Overview */}
          <Card className="mb-4">
            <Card.Body>
              <h4>Market Overview</h4>
              <p style={{ color: "#cccccc" }}>
                S&P 500: <span style={{ color: "#00c853" }}>+1.2%</span>
              </p>
              <p style={{ color: "#cccccc" }}>
                NASDAQ: <span style={{ color: "#00c853" }}>+0.8%</span>
              </p>
              <p style={{ color: "#cccccc" }}>
                DOW JONES: <span style={{ color: "#ff5252" }}>-0.3%</span>
              </p>
            </Card.Body>
          </Card>

          {/* Watchlist */}
          <Card>
            <Card.Body>
              <h4>Your Watchlist</h4>
              <Table striped bordered hover className="mt-3">
                <thead>
                  <tr>
                    <th style={{ color: "#ffffff" }}>Ticker</th>
                    <th style={{ color: "#ffffff" }}>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {watchlist.map((w, idx) => (
                    <tr key={idx}>
                      <td style={{ color: "#ffffff" }}>{w}</td>
                      <td>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => removeFromWatchlist(w)}
                        >
                          Remove
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
              {/* Use watchlistTicker here */}
              <Form
                className="d-flex mt-3"
                onSubmit={(e) => {
                  e.preventDefault();
                  addToWatchlist(watchlistTicker.toUpperCase());
                  setWatchlistTicker(""); // reset after adding
                }}
              >
                <Form.Control
                  type="text"
                  placeholder="Add to Watchlist"
                  value={watchlistTicker}
                  onChange={(e) => setWatchlistTicker(e.target.value)}
                  style={{ color: "#ffffff" }}
                />
                <Button variant="primary" type="submit" className="ms-2">
                  Add
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>

        <Col md={8}>
          {tickers.length > 0 ? (
            <>
              <Tabs
                defaultActiveKey={tickers[0]}
                id="stock-tabs"
                className="mt-4"
                fill
                variant="pills"
                style={{ backgroundColor: "#121212" }}
              >
                {tickers.map((ticker) => (
                  <Tab eventKey={ticker} title={ticker} key={ticker}>
                    <div className="mt-3">
                      {predictions[ticker] ? (
                        predictions[ticker].error ? (
                          <Alert variant="danger">
                            {predictions[ticker].error}
                          </Alert>
                        ) : (
                          <>
                            <h4 className="mt-3" style={{ color: "#ffffff" }}>
                              Predicted Close Price:{" "}
                              <span style={{ color: "#00c853" }}>
                                ${predictions[ticker].predicted_close}
                              </span>
                            </h4>
                            <h5
                              className="mt-4 mb-3"
                              style={{ color: "#ffffff" }}
                            >
                              Recommended Strategies:
                            </h5>
                            <StrategyList
                              strategies={
                                predictions[ticker].recommended_strategies
                              }
                            />

                            {/* Historical Chart */}
                            <HistoricalChart ticker={ticker} />

                            {/* Trade Simulation */}
                            <Card style={{ marginTop: "20px" }}>
                              <Card.Body>
                                <h5 style={{ color: "#ffffff" }}>
                                  Trade Simulation
                                </h5>
                                <Form onSubmit={handleTrade} className="mt-3">
                                  <Form.Group className="mb-3">
                                    <Form.Label>Ticker</Form.Label>
                                    <Form.Control
                                      type="text"
                                      value={tradeTicker}
                                      onChange={(e) =>
                                        setTradeTicker(
                                          e.target.value.toUpperCase()
                                        )
                                      }
                                      required
                                      style={{ color: "#ffffff" }}
                                    />
                                  </Form.Group>
                                  <Form.Group className="mb-3">
                                    <Form.Label>Action</Form.Label>
                                    <Form.Select
                                      value={tradeAction}
                                      onChange={(e) =>
                                        setTradeAction(e.target.value)
                                      }
                                      style={{ color: "#ffffff" }}
                                    >
                                      <option value="BUY">Buy</option>
                                      <option value="SELL">Sell</option>
                                    </Form.Select>
                                  </Form.Group>
                                  <Form.Group className="mb-3">
                                    <Form.Label>Quantity</Form.Label>
                                    <Form.Control
                                      type="number"
                                      min="1"
                                      value={tradeQuantity}
                                      onChange={(e) =>
                                        setTradeQuantity(
                                          parseInt(e.target.value)
                                        )
                                      }
                                      required
                                      style={{ color: "#ffffff" }}
                                    />
                                  </Form.Group>
                                  <Button
                                    variant="primary"
                                    type="submit"
                                    className="w-100"
                                  >
                                    Execute Trade
                                  </Button>
                                </Form>
                              </Card.Body>
                            </Card>
                          </>
                        )
                      ) : (
                        <Spinner animation="border" />
                      )}
                    </div>
                  </Tab>
                ))}
              </Tabs>
            </>
          ) : (
            <p className="mt-4" style={{ color: "#cccccc" }}>
              No tickers added yet. Use the Quick Actions above to add a ticker
              and view predictions.
            </p>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
