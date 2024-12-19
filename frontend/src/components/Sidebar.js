// Sidebar.js
import React from "react";
import { Nav } from "react-bootstrap";
import { Link } from "react-router-dom";
import { FaTachometerAlt, FaWallet, FaUserCog } from "react-icons/fa";

const Sidebar = () => {
  return (
    <div
      style={{
        backgroundColor: "#121212",
        width: "12vw",
        height: "100vh",
        position: "fixed",
        top: 0,
        left: 0,
        padding: "20px",
      }}
    >
      <Nav style={{marginTop:"30px"}} className="flex-column">
        <Nav.Link as={Link} to="/" style={{ color: "#ffffff" }}>
          <FaTachometerAlt style={{ marginRight: "8px" }} />
          Dashboard
        </Nav.Link>
        <Nav.Link as={Link} to="/portfolio" style={{ color: "#ffffff" }}>
          <FaWallet style={{ marginRight: "8px" }} />
          Portfolio
        </Nav.Link>
        <Nav.Link as={Link} to="/settings" style={{ color: "#ffffff" }}>
          <FaUserCog style={{ marginRight: "8px" }} />
          Settings
        </Nav.Link>
      </Nav>
    </div>
  );
};

export default Sidebar;
