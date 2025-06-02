# Jumia Deal Explorer – Intelligent Electronics Recommender

This project is a complete data pipeline and dashboard application designed to help users identify the best electronics deals on the Moroccan e-commerce platform Jumia. It also includes an initial price comparison module with Electroplanet, offering insights into pricing differences for equivalent products across vendors.

The system collects, cleans, analyzes, and visualizes product data in a structured and interactive way. The final result is a Streamlit web application where users can browse top deals by category, filter products by brand or price, and interact with a natural language chatbot.

## Features

- Automated scraping of electronic product listings from Jumia using Playwright and BeautifulSoup.
- Basic scraping module for Electroplanet for cross-vendor comparisons.
- Data cleaning and enrichment with product type classification (e.g., TV, smartphone, earpods).
- Fuzzy brand detection and normalization.
- Streamlit dashboard showing:
  - Top 5 deals by product category
  - Filterable tables with price and brand options
  - Visual analytics for price distribution
  - Natural language chatbot for querying products
- Cross-platform price comparison engine to match similar items and detect price gaps.

## Technologies

- Python 3.10+
- Playwright (headless browser automation)
- BeautifulSoup (HTML parsing)
- Pandas (data manipulation)
- RapidFuzz (string matching)
- Streamlit (dashboard and chatbot)
- Matplotlib (basic visualization)

## Installation

1. Clone the repository:

```

git clone [https://github.com/SalmaneSossey/ElectronicsHotDeals.git](https://github.com/SalmaneSossey/ElectronicsHotDeals.git)
cd ElectronicsHotDeals

```

2. Install required Python packages:

```

pip install -r requirements.txt

```

3. Run the scrapers:

```

python scraper\_jumia\_electronics.py
python scraper\_electroplanet.py

```

4. Clean the Jumia data:

```

python clean\_jumia\_data.py

```

5. Launch the dashboard:

```

streamlit run app1.py

```

## Project Structure

```

ElectronicsHotDeals/
│
├── app1.py                         # Streamlit dashboard
├── scraper\_jumia\_electronics.py   # Jumia scraper
├── scraper\_electroplanet.py       # Electroplanet scraper
├── clean\_jumia\_data.py            # Data cleaning and type detection
├── requirements.txt               # Python dependencies
├── README.md                      # Project documentation
├── jumia\_products\_raw\.csv
├── electroplanet\_products.jsonl
├── jumia\_products\_clean.csv

```

## Use Cases

This tool can be used to:

- Identify the best-priced TVs, phones, or audio accessories on Jumia
- Compare product prices between Jumia and Electroplanet
- Support informed purchasing decisions through visual data exploration
- Query available deals using natural language (e.g., "Samsung TV under 4000 Dhs")

## License

This project is open-source and available under the MIT License.

## Author

Developed by Salmane Sossey as part of the PFA project at ENSIAS (1st year, Artificial Intelligence and Data Engineering stream).


