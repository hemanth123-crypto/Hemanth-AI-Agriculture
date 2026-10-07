"""
scripts/generate_sample_data.py
Generates a realistic synthetic agricultural dataset matching the exact schema:
Crop, Crop_Year, Season, State, Area, Production, Yield, Fertilizer, Pesticide, N, P, K, pH, Temperature, Rainfall, Humidity

LABEL: SYNTHETIC TEST DATA (Generated for testing, development, and panel demonstration)
"""

import os
import random
import pandas as pd
import numpy as np

def generate_synthetic_crop_data(output_path: str = "data/sample/sample_crop_data.csv", num_records: int = 1500, seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)

    crops_profiles = {
        "Rice": {
            "seasons": ["Kharif", "Summer"],
            "states": ["Andhra Pradesh", "West Bengal", "Punjab", "Uttar Pradesh", "Odisha", "Tamil Nadu", "Bihar", "Assam"],
            "temp_range": (22.0, 34.0),
            "rain_range": (1000.0, 2400.0),
            "humidity_range": (65.0, 92.0),
            "ph_range": (5.5, 7.2),
            "n_range": (70, 130),
            "p_range": (30, 60),
            "k_range": (30, 60),
            "yield_base": 3.8,  # tonnes per hectare
            "fert_base": 140.0,
            "pest_base": 1.2,
        },
        "Wheat": {
            "seasons": ["Rabi"],
            "states": ["Punjab", "Haryana", "Uttar Pradesh", "Madhya Pradesh", "Rajasthan", "Bihar", "Gujarat"],
            "temp_range": (12.0, 25.0),
            "rain_range": (350.0, 750.0),
            "humidity_range": (45.0, 70.0),
            "ph_range": (6.0, 7.5),
            "n_range": (80, 140),
            "p_range": (40, 70),
            "k_range": (30, 50),
            "yield_base": 4.2,
            "fert_base": 150.0,
            "pest_base": 0.9,
        },
        "Maize": {
            "seasons": ["Kharif", "Rabi"],
            "states": ["Karnataka", "Andhra Pradesh", "Madhya Pradesh", "Maharashtra", "Bihar", "Rajasthan", "Tamil Nadu"],
            "temp_range": (18.0, 32.0),
            "rain_range": (600.0, 1100.0),
            "humidity_range": (50.0, 78.0),
            "ph_range": (5.8, 7.5),
            "n_range": (80, 120),
            "p_range": (35, 60),
            "k_range": (30, 50),
            "yield_base": 3.2,
            "fert_base": 120.0,
            "pest_base": 1.0,
        },
        "Cotton": {
            "seasons": ["Kharif"],
            "states": ["Gujarat", "Maharashtra", "Telangana", "Andhra Pradesh", "Haryana", "Punjab", "Karnataka"],
            "temp_range": (21.0, 35.0),
            "rain_range": (650.0, 1100.0),
            "humidity_range": (50.0, 75.0),
            "ph_range": (6.0, 8.0),
            "n_range": (90, 150),
            "p_range": (40, 75),
            "k_range": (40, 75),
            "yield_base": 2.4,
            "fert_base": 160.0,
            "pest_base": 2.2,
        },
        "Sugarcane": {
            "seasons": ["Whole Year"],
            "states": ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Andhra Pradesh", "Gujarat", "Bihar"],
            "temp_range": (20.0, 35.0),
            "rain_range": (1100.0, 2200.0),
            "humidity_range": (60.0, 85.0),
            "ph_range": (6.0, 7.8),
            "n_range": (120, 220),
            "p_range": (50, 90),
            "k_range": (60, 120),
            "yield_base": 70.0,
            "fert_base": 250.0,
            "pest_base": 3.0,
        },
        "Chickpea": {
            "seasons": ["Rabi"],
            "states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh", "Karnataka", "Andhra Pradesh"],
            "temp_range": (15.0, 28.0),
            "rain_range": (400.0, 800.0),
            "humidity_range": (40.0, 65.0),
            "ph_range": (6.0, 7.8),
            "n_range": (20, 45),
            "p_range": (40, 70),
            "k_range": (20, 40),
            "yield_base": 1.4,
            "fert_base": 60.0,
            "pest_base": 0.7,
        },
        "Groundnut": {
            "seasons": ["Kharif", "Rabi"],
            "states": ["Gujarat", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Rajasthan", "Maharashtra"],
            "temp_range": (22.0, 32.0),
            "rain_range": (500.0, 950.0),
            "humidity_range": (55.0, 75.0),
            "ph_range": (5.8, 7.2),
            "n_range": (20, 50),
            "p_range": (40, 70),
            "k_range": (30, 60),
            "yield_base": 1.9,
            "fert_base": 75.0,
            "pest_base": 0.8,
        },
        "Soybean": {
            "seasons": ["Kharif"],
            "states": ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka", "Telangana"],
            "temp_range": (20.0, 32.0),
            "rain_range": (650.0, 1050.0),
            "humidity_range": (60.0, 80.0),
            "ph_range": (6.0, 7.5),
            "n_range": (25, 55),
            "p_range": (45, 75),
            "k_range": (30, 50),
            "yield_base": 1.6,
            "fert_base": 70.0,
            "pest_base": 1.1,
        },
        "Mustard": {
            "seasons": ["Rabi"],
            "states": ["Rajasthan", "Haryana", "Madhya Pradesh", "Uttar Pradesh", "West Bengal", "Gujarat"],
            "temp_range": (10.0, 24.0),
            "rain_range": (300.0, 600.0),
            "humidity_range": (45.0, 70.0),
            "ph_range": (6.0, 7.5),
            "n_range": (60, 100),
            "p_range": (30, 50),
            "k_range": (20, 40),
            "yield_base": 1.5,
            "fert_base": 90.0,
            "pest_base": 0.8,
        },
        "Millets": {
            "seasons": ["Kharif"],
            "states": ["Rajasthan", "Maharashtra", "Karnataka", "Andhra Pradesh", "Gujarat", "Tamil Nadu", "Haryana"],
            "temp_range": (24.0, 36.0),
            "rain_range": (350.0, 700.0),
            "humidity_range": (35.0, 65.0),
            "ph_range": (5.5, 8.0),
            "n_range": (40, 80),
            "p_range": (20, 45),
            "k_range": (20, 40),
            "yield_base": 1.3,
            "fert_base": 65.0,
            "pest_base": 0.5,
        },
        "Barley": {
            "seasons": ["Rabi"],
            "states": ["Rajasthan", "Uttar Pradesh", "Madhya Pradesh", "Haryana", "Punjab"],
            "temp_range": (12.0, 25.0),
            "rain_range": (350.0, 650.0),
            "humidity_range": (40.0, 65.0),
            "ph_range": (6.2, 7.8),
            "n_range": (60, 90),
            "p_range": (30, 50),
            "k_range": (20, 35),
            "yield_base": 2.8,
            "fert_base": 100.0,
            "pest_base": 0.6,
        },
        "Jute": {
            "seasons": ["Kharif"],
            "states": ["West Bengal", "Bihar", "Assam", "Odisha", "Andhra Pradesh"],
            "temp_range": (24.0, 36.0),
            "rain_range": (1200.0, 2200.0),
            "humidity_range": (70.0, 95.0),
            "ph_range": (5.0, 7.2),
            "n_range": (60, 100),
            "p_range": (30, 50),
            "k_range": (40, 70),
            "yield_base": 2.6,
            "fert_base": 110.0,
            "pest_base": 1.0,
        }
    }

    years = list(range(2012, 2024))
    records = []

    crop_names = list(crops_profiles.keys())

    for i in range(num_records):
        crop = random.choice(crop_names)
        prof = crops_profiles[crop]

        year = random.choice(years)
        season = random.choice(prof["seasons"])
        state = random.choice(prof["states"])

        # Weather with subtle variations
        temp = round(random.uniform(*prof["temp_range"]) + np.random.normal(0, 1.2), 1)
        temp = max(5.0, min(48.0, temp))

        rain = round(random.uniform(*prof["rain_range"]) + np.random.normal(0, 40), 1)
        rain = max(100.0, rain)

        humidity = round(random.uniform(*prof["humidity_range"]) + np.random.normal(0, 3), 1)
        humidity = max(20.0, min(99.0, humidity))

        # Soil parameters
        ph = round(random.uniform(*prof["ph_range"]) + np.random.normal(0, 0.25), 2)
        ph = max(4.0, min(9.0, ph))

        n_val = int(random.uniform(*prof["n_range"]) + np.random.normal(0, 5))
        n_val = max(10, n_val)

        p_val = int(random.uniform(*prof["p_range"]) + np.random.normal(0, 3))
        p_val = max(10, p_val)

        k_val = int(random.uniform(*prof["k_range"]) + np.random.normal(0, 3))
        k_val = max(10, k_val)

        # Farming area (hectares)
        area = round(random.uniform(500, 25000), 1)

        # Yield factor based on optimal conditions
        # Deviation penalties
        ph_mid = (prof["ph_range"][0] + prof["ph_range"][1]) / 2.0
        ph_factor = max(0.6, 1.0 - 0.2 * abs(ph - ph_mid))

        rain_mid = (prof["rain_range"][0] + prof["rain_range"][1]) / 2.0
        rain_factor = max(0.65, 1.0 - 0.0003 * abs(rain - rain_mid))

        fert = round(prof["fert_base"] * random.uniform(0.85, 1.25), 1)
        pest = round(prof["pest_base"] * random.uniform(0.80, 1.30), 2)

        # Yield calculation
        yield_val = prof["yield_base"] * ph_factor * rain_factor * (1.0 + np.random.normal(0, 0.08))
        yield_val = round(max(0.2, yield_val), 2)

        # Production = Area * Yield
        production = round(area * yield_val, 1)

        records.append({
            "Crop": crop,
            "Crop_Year": year,
            "Season": season,
            "State": state,
            "Area": area,
            "Production": production,
            "Yield": yield_val,
            "Fertilizer": fert,
            "Pesticide": pest,
            "N": n_val,
            "P": p_val,
            "K": k_val,
            "pH": ph,
            "Temperature": temp,
            "Rainfall": rain,
            "Humidity": humidity
        })

    df = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[SYNTHETIC TEST DATA] Generated {len(df)} records saved to '{output_path}'.")
    return df

if __name__ == "__main__":
    generate_synthetic_crop_data()
