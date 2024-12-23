import React from "react";
import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");

  if (!token) {
    return <Navigate to="/login" />;
  }

  try {
    const decoded = jwtDecode(token);
    if (decoded.exp * 1000 < Date.now()) {
      // Token expired
      localStorage.removeItem("token");
      return <Navigate to="/login" />;
    }
  } catch (error) {
    // Invalid token
    localStorage.removeItem("token");
    return <Navigate to="/login" />;
  }

  return children;
};

export default PrivateRoute;
