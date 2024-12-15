import unittest
import pandas as pd
from data.preprocessing import preprocess_data

class TestPreprocessing(unittest.TestCase):
    def test_preprocess_data(self):
        # Create mock data
        stock_data = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Close': [150, 152],
            'Volume': [1000000, 1100000]
        })
        
        options_data = pd.DataFrame({
            'lastTradeDate': ['2023-01-01', '2023-01-02'],
            'strike': [155, 160],
            'lastPrice': [5, 3],
            'optionType': ['call', 'put'],
            'expirationDate': ['2023-02-01', '2023-02-01']
        })
        
        merged_data = preprocess_data(stock_data, options_data)
        
        # Assertions
        self.assertEqual(len(merged_data), 2)
        self.assertIn('T', merged_data.columns)
        self.assertIn('moneyness', merged_data.columns)

if __name__ == '__main__':
    unittest.main()
