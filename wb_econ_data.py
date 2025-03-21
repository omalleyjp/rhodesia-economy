# wb_econ_data.py
# Simplified World Bank economic indicators with a data retrieval class

import requests
import pandas as pd

# Step 1: Map simplified names to World Bank codes and definitions
econ_indicators = {
    "GDP_MKTP": {
        "code": "NY.GDP.MKTP.CD",
        "definition": "Total economic output of a country in current US dollars (Gross Domestic Product)."
    },
    "GDP_PCAP": {
        "code": "NY.GDP.PCAP.CD",
        "definition": "Average economic output per person in current US dollars (GDP per capita)."
    },
    "EXPORTS": {
        "code": "NE.EXP.GNFS.CD",
        "definition": "Value of goods and services a country sells to the rest of the world (Exports)."
    },
    "IMPORTS": {
        "code": "NE.IMP.GNFS.CD",
        "definition": "Value of goods and services a country buys from the rest of the world (Imports)."
    },
    "TRADE_OPEN": {
        "code": "NE.TRD.GNFS.ZS",
        "definition": "Sum of exports and imports as a percentage of GDP (Trade openness)."
    },
    "GNI_MKTP": {
        "code": "NY.GNP.MKTP.CD",
        "definition": "Total income earned by a country’s residents, including foreign income, in current US dollars (Gross National Income)."
    },
    "GNI_PCAP": {
        "code": "NY.GNP.PCAP.CD",
        "definition": "Average income per person, including foreign earnings, in current US dollars (GNI per capita)."
    },
    "CONSUMPTION": {
        "code": "NE.CON.TOTL.CD",
        "definition": "Total spending by households and government on goods and services in current US dollars (Consumption)."
    },
    "AGRI_VALUE": {
        "code": "NV.AGR.TOTL.CD",
        "definition": "Value added by agriculture, forestry, and fishing to the economy in current US dollars."
    },
    "IND_VALUE": {
        "code": "NV.IND.TOTL.CD",
        "definition": "Value added by industries like manufacturing and mining to the economy in current US dollars."
    },
    "SERV_VALUE": {
        "code": "NV.SRV.TOTL.CD",
        "definition": "Value added by service sectors like retail and education to the economy in current US dollars."
    },
    "FDI_INFLOW": {
        "code": "BX.KLT.DINV.CD.WD",
        "definition": "Money invested into a country from abroad in current US dollars (Foreign Direct Investment, net inflows)."
    },
    "INFLATION": {
        "code": "FP.CPI.TOTL.ZG",
        "definition": "Annual percentage change in the cost of goods and services (Inflation, consumer prices)."
    },
    "DOM_CREDIT": {
        "code": "FS.AST.DOMS.GD.ZS",
        "definition": "Credit provided by banks and financial institutions as a percentage of GDP (Domestic credit)."
    },
    "UNEMPLOYMENT": {
        "code": "SL.UEM.TOTL.ZS",
        "definition": "Percentage of the labor force without jobs (Unemployment rate)."
    },
    "POPULATION": {
        "code": "SP.POP.TOTL",
        "definition": "Total number of people living in a country (Population)."
    },
    "LIFE_EXP": {
        "code": "SP.DYN.LE00.IN",
        "definition": "Average number of years a newborn is expected to live (Life expectancy at birth)."
    },
}

# Step 2: Define the EconData class for fetching data
class EconData:
    def __init__(self):
        self.indicators = econ_indicators
    
    def get(self, country_code, indicator, date_range="1960:2023"):
        """
        Fetch World Bank data for a given country, indicator, and date range.
        
        Args:
            country_code (str or list): ISO3 country code(s) (e.g., 'AGO' or ['AGO', 'BDI'])
            indicator (str): Simplified indicator name (e.g., 'GDP_MKTP')
            date_range (str): Years in 'start:end' format (e.g., '1960:2023')
        
        Returns:
            pandas.DataFrame: Data with columns 'country', 'year', 'value'
        """
        # Validate indicator
        if indicator not in self.indicators:
            raise ValueError(f"Indicator '{indicator}' not found. Available: {list(self.indicators.keys())}")
        
        wb_code = self.indicators[indicator]["code"]
        
        # Handle single or multiple countries
        if isinstance(country_code, str):
            country_codes = country_code
        elif isinstance(country_code, list):
            country_codes = ";".join(country_code)
        else:
            raise ValueError("country_code must be a string or list of strings")
        
        # Fetch data from World Bank API
        all_data = []
        page = 1
        while True:
            url = (f"https://api.worldbank.org/v2/country/{country_codes}/indicator/{wb_code}"
                   f"?date={date_range}&format=json&per_page=1000&page={page}")
            response = requests.get(url)
            
            if response.status_code != 200:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
            
            json_data = response.json()
            if not isinstance(json_data, list) or len(json_data) < 2 or 'message' in json_data[0]:
                print(f"Error fetching {indicator}: {json_data}")
                return None
            
            metadata, data = json_data[0], json_data[1]
            all_data.extend(data)
            
            if page >= metadata['pages']:
                break
            page += 1
        
        # Convert to DataFrame
        if not all_data:
            print(f"No data retrieved for {indicator} in {country_codes}")
            return None
        
        df = pd.DataFrame(all_data)
        df['indicator'] = df['indicator'].apply(lambda x: x['id'] if isinstance(x, dict) else x)
        df = df[['countryiso3code', 'date', 'value']].dropna(subset=['value'])
        df.columns = ['country', 'year', 'value']
        
        return df

    def get_definition(self, indicator):
        """Return the definition for a given indicator."""
        if indicator not in self.indicators:
            return f"Indicator '{indicator}' not found."
        return self.indicators[indicator]["definition"]