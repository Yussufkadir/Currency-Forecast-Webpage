import requests
import asyncio
import aiohttp
from typing import Dict, Optional
from datetime import datetime

class ExchangeRateAPI:
    """
    Service to fetch live exchange rates from various APIs
    """
    
    def __init__(self):
        # Free APIs (no key required)
        self.free_apis = {
            'exchangerate-api': 'https://api.exchangerate-api.com/v4/latest/',
            'fixer-free': 'https://api.fixer.io/latest',  # Requires free API key
            'currencylayer-free': 'http://api.currencylayer.com/live'  # Requires free API key
        }
        
        # API keys (get these from respective services)
        self.api_keys = {
            'fixer': None,  # Sign up at https://fixer.io/
            'currencylayer': None,  # Sign up at https://currencylayer.com/
        }
    
    async def get_live_rates_exchangerate_api(self, base_currency: str = 'USD') -> Optional[Dict]:
        """
        Fetch live rates from exchangerate-api.com (free, no key required)
        """
        try:
            url = f"https://api.exchangerate-api.com/v4/latest/{base_currency}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'base': data['base'],
                            'rates': data['rates'],
                            'timestamp': datetime.now().isoformat(),
                            'source': 'exchangerate-api'
                        }
        except Exception as e:
            print(f"Error fetching from exchangerate-api: {e}")
            return None
    
    async def get_live_rates_fixer(self, base_currency: str = 'USD') -> Optional[Dict]:
        """
        Fetch live rates from Fixer API (requires free API key)
        """
        if not self.api_keys['fixer']:
            return None
            
        try:
            url = f"http://data.fixer.io/api/latest"
            params = {
                'access_key': self.api_keys['fixer'],
                'base': base_currency,
                'format': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success'):
                            return {
                                'base': data['base'],
                                'rates': data['rates'],
                                'timestamp': datetime.fromtimestamp(data['timestamp']).isoformat(),
                                'source': 'fixer'
                            }
        except Exception as e:
            print(f"Error fetching from Fixer: {e}")
            return None
    
    def get_currency_pair_rate(self, rates_data: Dict, pair: str) -> Optional[float]:
        """
        Extract specific currency pair rate from rates data
        Example: pair = 'EURUSD' -> gets EUR/USD rate
        """
        if not rates_data or 'rates' not in rates_data:
            return None
            
        # Parse pair (e.g., 'EURUSD' -> base='EUR', quote='USD')
        if len(pair) == 6:
            base = pair[:3]
            quote = pair[3:]
            
            rates = rates_data['rates']
            base_currency = rates_data['base']
            
            # If both currencies are in rates
            if base in rates and quote in rates:
                return rates[quote] / rates[base]
            # If base is the base currency of the API
            elif base == base_currency and quote in rates:
                return rates[quote]
            # If quote is the base currency of the API
            elif quote == base_currency and base in rates:
                return 1 / rates[base]
                
        return None

# Global instance
exchange_api = ExchangeRateAPI()