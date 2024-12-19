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

  const [watchlistSort, setWatchlistSort] = useState("alphabetical");
  const [watchlistFilter, setWatchlistFilter] = useState("all");
  const [watchlistTicker, setWatchlistTicker] = useState("");


  // Mock Expiration Dates
  const [selectedExpiration, setSelectedExpiration] = useState("2024-12-31");
  const expirationDates = [
    "2024-12-31",
    "2025-01-15",
    "2025-02-28",
    "2025-03-31",
  ];

  // Mock Options Chain Data
  // This is mock data for demonstration purposes.
  // To use real data, you would fetch from your API and set it in state.
  const mockOptionsChain = [
    { strike: 150, type: "Call", premium: 4.5, delta: 0.45, theta: -0.02 },
    { strike: 155, type: "Call", premium: 2.3, delta: 0.30, theta: -0.015 },
    { strike: 140, type: "Put", premium: 3.7, delta: -0.40, theta: -0.018 },
    { strike: 145, type: "Put", premium: 5.1, delta: -0.55, theta: -0.025 },
  ];

  // News
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
    // if (ticker && !tickers.includes(ticker)) {
    //   setTickers([...tickers, ticker]);
    //   setSelectedTicker("");
    //   await fetchPrediction(ticker);
    // }
    /*       USE THE CODE BELOW TO TEST THAT THE OPTIONS CHART SHOWS FOR QUICK ADD STOCKS     */
    if (ticker && !tickers.includes(ticker)) {
      setTickers([...tickers, ticker]);
      setSelectedTicker("");
      // Instead of calling the API for now, set mock predictions
      setPredictions((prev) => ({
        ...prev,
        [ticker]: {
          predicted_close: 123.45,
          recommended_strategies: [
            { name: "Call Spread", confidence: "High", details: "Mock strategy details..." },
          ],
        },
      }));
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
    if (t && !watchlist.includes(t)) {
      setWatchlist([...watchlist, t]);
    }
  };

  const removeFromWatchlist = (t) => {
    setWatchlist(watchlist.filter((item) => item !== t));
  };

  const sortedWatchlist = [...watchlist].sort((a, b) => {
    if (watchlistSort === "alphabetical") {
      return a.localeCompare(b);
    }
    return 0;
  });

  // Mock daily % change function
  // In a real scenario, you'd fetch this data from your API.
  const getMockPercentChange = (ticker) => {
    // Just generate a random percentage between -5% and +5%
    const randomChange = (Math.random() * 10 - 5).toFixed(2);
    const isPositive = parseFloat(randomChange) > 0;
    return (
      <span style={{ color: isPositive ? "#00c853" : "#ff5252" }}>
        {randomChange}%
      </span>
    );
  };

  return (
    <Container fluid style={{ width: "88vw", marginInline: "12vw", paddingTop: "30px" }}>
      <h2 className="mb-4" style={{ color: "#ffffff" }}>
        Dashboard
      </h2>
      <p style={{ color: "#cccccc" }}>
        Data Sources: Alpha Vantage (Price), Yahoo Finance (Options), NewsAPI (News)
      </p>
      <Row>
        <Col md={8}>
          <Card className="mb-4" style={{ backgroundColor: "#1e1e1e" }}>
            <Card.Body>
              <h4 style={{ color: "#ffffff" }}>Quick Actions</h4>
              <Form 
                className="d-flex mt-3 mb-3"
                onSubmit={(e) => {
                  e.preventDefault();
                  handleAddTicker();
                }}
              >
                <Form.Control
                  type="text"
                  placeholder="Enter Ticker Symbol"
                  value={selectedTicker}
                  onChange={(e) => {
                    const val = e.target.value.toUpperCase().slice(0,4);
                    setSelectedTicker(val);
                  }}
                  style={{ color: "#ffffff", backgroundColor: "#121212" }}
                />
                <Button variant="primary" className="ms-2" onClick={handleAddTicker}>
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
                  <div className="d-flex mb-3" style={{ gap: "10px" }}>
                    <Form.Select
                      value={watchlistSort}
                      onChange={(e) => setWatchlistSort(e.target.value)}
                      style={{ backgroundColor: "#121212", color: "#ffffff", width: "40%" }}
                    >
                      <option value="alphabetical">Sort: A-Z</option>
                      {/* You can add other sort options as needed */}
                    </Form.Select>
                    <Form.Select
                      value={watchlistFilter}
                      onChange={(e) => setWatchlistFilter(e.target.value)}
                      style={{ backgroundColor: "#121212", color: "#ffffff", width: "40%" }}
                    >
                      <option value="all">Filter: All</option>
                      <option value="tech">Filter: Tech</option>
                      <option value="finance">Filter: Financials</option>
                      <option value="healthcare">Filter: Healthcare</option>
                      <option value="energy">Filter: Energy</option>
                      <option value="realestate">Filter: Real Estate</option>
                      <option value="utilities">Filter: Utilities</option>
                    </Form.Select>
                  </div>

                  <Table
                    className="mt-3 table-dark table-borderless"
                    style={{ backgroundColor: "#1e1e2e", color: "#ffffff", borderRadius: "8px", overflow: "hidden" }}
                  >
                    <thead style={{ backgroundColor: "#2a2a3e" }}>
                      <tr style={{ borderBottom: "2px solid #44475a" }}>
                        <th style={{ padding: "12px", textAlign: "left" }}>Ticker</th>
                        <th style={{ padding: "12px", textAlign: "left" }}>Daily % Change</th>
                        <th style={{ padding: "12px", textAlign: "left" }}>Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sortedWatchlist
                        .filter((w) => (watchlistFilter === "all" ? true : true /* filter logic here if desired */))
                        .map((w, idx) => (
                          <tr
                            key={idx}
                            style={{ borderBottom: "1px solid #44475a", transition: "background-color 0.3s" }}
                            className="hover-row"
                          >
                            <td style={{ padding: "12px", color: "#f8f8f2" }}>{w}</td>
                            <td style={{ padding: "12px" }}>
                              {getMockPercentChange(w)}
                            </td>
                            <td style={{ padding: "12px" }}>
                              <Button
                                variant="outline-danger"
                                size="sm"
                                onClick={() => removeFromWatchlist(w)}
                                style={{ borderColor: "#ff5555", color: "#ff5555" }}
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

          {/* Ticker Tabs with Options Chain */}
          {tickers.length > 0 ? (
            <Tabs
              defaultActiveKey={tickers[0]}
              id="stock-tabs"
              className="mt-4"
              fill
              variant="pills"
              style={{ backgroundColor: "#121212", justifyContent: "flex-start" }}
            >
              {tickers.map((ticker) => (
                <Tab
                  eventKey={ticker}
                  title={
                    <span style={{ fontSize: "1.2rem", textAlign: "left", minWidth: "100px", display: "inline-block" }}>
                      {ticker}
                    </span>
                  }
                  key={ticker}
                >
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
                          <h5 className="mt-4 mb-3" style={{ fontSize: "1.2rem", color: "#ffffff" }}>
                            Recommended Strategies:
                          </h5>
                          <div style={{ backgroundColor: "#1e1e1e", padding: "15px", borderRadius: "8px" }}>
                          <Table
                            striped
                            bordered
                            hover
                            variant="dark"
                            style={{ backgroundColor: "#1e1e1e" }}
                          >
                            <thead>
                              <tr style={{ borderBottom: "2px solid #44475a" }}>
                                <th style={{ color: "#ffffff" }}>Strategy Name</th>
                                <th style={{ color: "#ffffff" }}>Confidence</th>
                                <th style={{ color: "#ffffff" }}>Execution Steps</th>
                              </tr>
                            </thead>
                            <tbody>
                              {predictions[ticker].recommended_strategies && predictions[ticker].recommended_strategies.length > 0 ? (
                                predictions[ticker].recommended_strategies.map((strategy, index) => (
                                  <tr key={index} style={{ borderBottom: "1px solid #44475a" }}>
                                    <td style={{ color: "#f8f8f2" }}>{strategy.name}</td>
                                    <td style={{ color: "#f8f8f2" }}>{strategy.confidence}</td>
                                    <td style={{ color: "#f8f8f2" }}>{strategy.details}</td>
                                  </tr>
                                ))
                              ) : (
                                <tr>
                                  <td colSpan="2" style={{ color: "#f8f8f2" }}>No strategies available</td>
                                </tr>
                              )}
                            </tbody>
                          </Table>
                          </div>

                          {/* Expiration Date Filter */}
                          <div className="d-flex mt-4 mb-2 align-items-center">
                            <span className="me-2">Expiration:</span>
                            <Form.Select
                              value={selectedExpiration}
                              onChange={(e) => setSelectedExpiration(e.target.value)}
                              style={{
                                width: "200px",
                                backgroundColor: "#121212",
                                color: "#ffffff",
                              }}
                            >
                              {expirationDates.map((date) => (
                                <option key={date} value={date}>
                                  {date}
                                </option>
                              ))}
                            </Form.Select>
                          </div>

                          {/* Options Chain Table (Mock Data) */}
                          {/* Currently showing mock data. To use real data, replace `mockOptionsChain` with API response data. */}
                          <h5 className="mt-3 mb-2">Options Chain (Mock Data)</h5>
                          <Table
                            striped
                            bordered
                            hover
                            variant="dark"
                            style={{ backgroundColor: "#1e1e1e" }}
                          >
                            <thead>
                              <tr>
                                <th>Strike</th>
                                <th>Type</th>
                                <th>Premium</th>
                                <th>Delta</th>
                                <th>Theta</th>
                              </tr>
                            </thead>
                            <tbody>
                              {mockOptionsChain.map((option, idx) => (
                                <tr
                                  key={idx}
                                  style={{ cursor: "pointer" }}
                                  title="Click for more details on Greeks"
                                  onClick={() =>
                                    alert(`Option Details:
                                      Strike: ${option.strike}
                                      Type: ${option.type}
                                      Premium: $${option.premium}
                                      Delta: ${option.delta}
                                      Theta: ${option.theta}
                                      Additional Greeks and IV would appear here.`
                                    )
                                  }
                                >
                                  <td>{option.strike}</td>
                                  <td>{option.type}</td>
                                  <td>${option.premium}</td>
                                  <td>{option.delta}</td>
                                  <td>{option.theta}</td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
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
