// Settings.js
import React, { useState } from "react";
import { Container, Form, Button, Card } from "react-bootstrap";

const Settings = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);

  const handleSave = (e) => {
    e.preventDefault();
    // Save preferences locally or via API
    alert("Settings saved!");
  };

  return (
    <Container
      fluid
      style={{ marginLeft: "220px", paddingTop: "30px", color: "#ffffff" }}
    >
      <h2>Settings</h2>
      <Card style={{ marginTop: "20px" }}>
        <Card.Body>
          <Form onSubmit={handleSave}>
            <Form.Group className="mb-3">
              <Form.Label>Theme</Form.Label>
              <Form.Check
                type="switch"
                id="dark-mode-switch"
                label="Dark Mode"
                checked={darkMode}
                onChange={() => setDarkMode(!darkMode)}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Notifications</Form.Label>
              <Form.Check
                type="checkbox"
                label="Enable Price Alerts"
                checked={notifications}
                onChange={() => setNotifications(!notifications)}
              />
            </Form.Group>

            <Button variant="primary" type="submit" className="w-100">
              Save Settings
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default Settings;
