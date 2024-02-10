import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Generate data for 930 days
start_date = datetime(2021, 1, 1)  # Start date
end_date = start_date + timedelta(days=930)  # End date

date_range = pd.date_range(start=start_date, end=end_date, freq="D")

# Generate wave-like CLOSE values
close_values = np.sin(np.linspace(0, 40 * np.pi, len(date_range))) * 40 + 120

data = {
    "DATE": date_range.strftime("%Y-%m-%d"),
    "OPEN": [100.0] * len(date_range),
    "CLOSE": close_values,
    "HIGH": close_values + 10,
    "LOW": close_values - 10,
}

df = pd.DataFrame(data)

# Save to CSV
df.to_csv("mocked_data.csv", index=False)

print("Data saved to mocked_data.csv")
