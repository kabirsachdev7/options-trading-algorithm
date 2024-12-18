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
  Card,
  Row,
  Col,
  Table,
} from "react-bootstrap";
import StrategyList from "./StrategyList";

const Dashboard = () => {
  const [tickers, setTickers] = useState([]);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [predictions, setPredictions] = useState({});
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [watchlist, setWatchlist] = useState(["AAPL", "TSLA"]);

  // New state for News
  const [news, setNews] = useState([]);

  useEffect(() => {
    // Fetch news updates
    const fetchNews = async () => {
      try {
        const token = localStorage.getItem("token");
        const response = await axios.get(
          `${process.env.REACT_APP_API_URL}/news`,
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        setNews(response.data);
      } catch (err) {
        console.error("Failed to fetch news:", err);
      }
    };
    fetchNews();
  }, []);

  const handleAddTicker = async () => {
    const ticker = selectedTicker.trim().toUpperCase();
    if (ticker && !tickers.includes(ticker)) {
      setTickers([...tickers, ticker]);
      setSelectedTicker("");
      await fetchPrediction(ticker);
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
      setError(err.response ? err.response.data.detail : "Server Error");
      setLoading(false);
    }
  };

  const addToWatchlist = (t) => {
    if (t && !watchlist.includes(t)) setWatchlist([...watchlist, t]);
  };

  const removeFromWatchlist = (t) => {
    setWatchlist(watchlist.filter((item) => item !== t));
  };

  const [watchlistTicker, setWatchlistTicker] = useState("");

  return (
    <Container fluid style={{ marginLeft: "220px", paddingTop: "30px" }}>
      <h2 className="mb-4" style={{ color: "#ffffff" }}>
        Options Trading Dashboard
      </h2>
      <p style={{ color: "#cccccc" }}>
        Data Sources: Alpha Vantage (Price), Yahoo Finance (Options), NewsAPI
        (News)
      </p>
      <Row>
        <Col md={8}>
          <Card className="mb-4" style={{ backgroundColor: "#1e1e1e" }}>
            <Card.Body>
              <h4 style={{ color: "#ffffff" }}>Quick Actions</h4>
              <Form className="d-flex mt-3 mb-3">
                <Form.Control
                  type="text"
                  placeholder="Enter Ticker Symbol"
                  value={selectedTicker}
                  onChange={(e) => setSelectedTicker(e.target.value)}
                  style={{ color: "#ffffff", backgroundColor: "#121212" }}
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
            <Col md={6}>
              <Card className="mb-4" style={{ backgroundColor: "#1e1e1e" }}>
                <Card.Body>
                  <h4 style={{ color: "#ffffff" }}>Market Overview</h4>
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
            </Col>
            <Col md={6}>
              <Card style={{ backgroundColor: "#1e1e1e" }}>
                <Card.Body>
                  <h4 style={{ color: "#ffffff" }}>Your Watchlist</h4>
                  <Table
                    striped
                    bordered
                    hover
                    className="mt-3"
                    style={{ color: "#ffffff" }}
                  >
                    <thead>
                      <tr>
                        <th>Ticker</th>
                        <th>Action</th>
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
                  <Form
                    className="d-flex mt-3"
                    onSubmit={(e) => {
                      e.preventDefault();
                      addToWatchlist(watchlistTicker.toUpperCase());
                      setWatchlistTicker("");
                    }}
                  >
                    <Form.Control
                      type="text"
                      placeholder="Add to Watchlist"
                      value={watchlistTicker}
                      onChange={(e) => setWatchlistTicker(e.target.value)}
                      style={{ color: "#ffffff", backgroundColor: "#121212" }}
                    />
                    <Button variant="primary" type="submit" className="ms-2">
                      Add
                    </Button>
                  </Form>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          {tickers.length > 0 ? (
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
                  <div className="mt-3" style={{ color: "#ffffff" }}>
                    {predictions[ticker] ? (
                      predictions[ticker].error ? (
                        <Alert variant="danger">
                          {predictions[ticker].error}
                        </Alert>
                      ) : (
                        <>
                          <h4 className="mt-3">
                            Predicted Close Price:{" "}
                            <span style={{ color: "#00c853" }}>
                              ${predictions[ticker].predicted_close}
                            </span>
                          </h4>
                          <h5 className="mt-4 mb-3">Recommended Strategies:</h5>
                          <StrategyList
                            strategies={
                              predictions[ticker].recommended_strategies
                            }
                          />
                          {/* Charts and Trade Simulation as previously implemented */}
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
            <p className="mt-4" style={{ color: "#cccccc" }}>
              No tickers added yet. Use the Quick Actions above to add a ticker
              and view predictions.
            </p>
          )}
        </Col>

        {/* News Sidebar */}
        <Col
          md={4}
          style={{
            backgroundColor: "#1e1e1e",
            height: "100vh",
            overflowY: "auto",
          }}
        >
          <h4
            style={{ color: "#ffffff", marginTop: "20px", marginLeft: "10px" }}
          >
            Live Business News
          </h4>
          {news.length === 0 ? (
            <p style={{ color: "#cccccc", marginLeft: "10px" }}>
              No news available.
            </p>
          ) : (
            news.map((article, idx) => (
              <Card
                key={idx}
                style={{ backgroundColor: "#121212", margin: "10px" }}
              >
                <Card.Body>
                  <Card.Title style={{ color: "#ffffff" }}>
                    {article.title}
                  </Card.Title>
                  <Card.Text style={{ color: "#cccccc" }}>
                    {article.description}
                  </Card.Text>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{ color: "#00c853" }}
                  >
                    Read More
                  </a>
                  <p
                    style={{
                      color: "#999999",
                      fontSize: "0.8em",
                      marginTop: "10px",
                    }}
                  >
                    Source: {article.source}
                  </p>
                </Card.Body>
              </Card>
            ))
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Dashboard;
