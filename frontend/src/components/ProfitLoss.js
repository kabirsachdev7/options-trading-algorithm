import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ProfitLoss = ({ holding }) => {
  const [currentPrice, setCurrentPrice] = useState(null);

  useEffect(() => {
    const fetchPrice = async () => {
      try {
        const response = await axios.get(`${process.env.REACT_APP_API_URL}/price/${holding.ticker}`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        setPrice(response.data.current_price);
      } catch (err) {
        setCurrentPrice(null);
      }
    };
    fetchPrice();
  }, [holding.ticker]);

  if (currentPrice === null) return 'N/A';

  const profitLoss = (currentPrice - holding.purchase_price) * holding.quantity;
  return (
    <span style={{ color: profitLoss >= 0 ? 'green' : 'red' }}>
      ${profitLoss.toFixed(2)}
    </span>
  );
};

export default ProfitLoss;
