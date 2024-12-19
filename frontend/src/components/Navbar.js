import React from "react";
import { Navbar, Nav, Container } from "react-bootstrap";
import { Link, useNavigate } from "react-router-dom";

const NavigationBar = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem("token");

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <Navbar expand="lg" style={{ backgroundColor: "#121212" }}>
      <Container>
        <Navbar.Brand as={Link} to="/" style={{ color: "#00c853" }}>
          Options Trading Platform
        </Navbar.Brand>
        <Navbar.Toggle
          aria-controls="basic-navbar-nav"
          style={{ color: "#ffffff" }}
        />
        <Navbar.Collapse id="basic-navbar-nav">
          {token && (
            <Nav className="me-auto">
              <Nav.Link as={Link} to="/" style={{ color: "#ffffff" }}>
                Dashboard
              </Nav.Link>
              <Nav.Link as={Link} to="/portfolio" style={{ color: "#ffffff" }}>
                Portfolio
              </Nav.Link>
            </Nav>
          )}
          <Nav>
            {token ? (
              <Nav.Link onClick={handleLogout} style={{ color: "#ffffff" }}>
                Logout
              </Nav.Link>
            ) : (
              <>
                <Nav.Link as={Link} to="/login" style={{ color: "#ffffff" }}>
                  Login
                </Nav.Link>
                <Nav.Link as={Link} to="/register" style={{ color: "#ffffff" }}>
                  Register
                </Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default NavigationBar;
