import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Recommendations() {
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get('/api/recommend');
      setRecommendations(response.data.recommendations);
    } catch (error) {
      console.error("Error fetching recommendations:", error);
    }
  };

  return (
    <div>
      <h2>Recommended Strategies</h2>
      {recommendations.map((strategy, index) => (
        <div key={index}>
          <h3>{strategy.type}</h3>
          <p>Parameters: {JSON.stringify(strategy.params)}</p>
        </div>
      ))}
    </div>
  );
}

export default Recommendations;
