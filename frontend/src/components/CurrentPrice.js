import { useState, useEffect } from "react";
import axios from "axios";

const CurrentPrice = ({ ticker }) => {
  const [price, setPrice] = useState(null);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const response = await axios.get(
          `${process.env.REACT_APP_API_URL}/price/${ticker}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        setPrice(response.data.current_price);
      } catch (err) {
        setPrice("N/A");
      }
    };
    fetchPrice();
  }, [ticker]);

  return price !== null ? `$${price}` : "Loading...";
};

export default CurrentPrice;
