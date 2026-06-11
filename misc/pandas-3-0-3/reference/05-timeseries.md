# Time Series

## Contents
- Timestamps and Timedeltas
- DatetimeIndex
- Generating Ranges (date_range)
- Resampling
- Time Zone Handling
- DateOffset Objects

## Timestamps and Timedeltas

```python
# Single timestamp
ts = pd.Timestamp("2024-01-15 10:30:00")

# Parse from string
ts = pd.to_datetime("2024-01-15")

# Timedelta
td = pd.Timedelta("3 days 2 hours")
td = pd.Timedelta(days=3, hours=2)

# Arithmetic
ts + td              # later timestamp
ts - ts2             # Timedelta result
```

## DatetimeIndex

Create a time-based index for time-indexed data:

```python
# From parsing during read
df = pd.read_csv("data.csv", parse_dates=["date"], index_col="date")

# Manual creation
idx = pd.DatetimeIndex(["2024-01-01", "2024-01-02", "2024-01-03"])
df = pd.DataFrame({"value": [1, 2, 3]}, index=idx)

# Time-based indexing
df["2024-01"]           # all of January
df["2024-01-01":"2024-01-31"]  # date range slice
df.loc["2024-01-01"]    # single day
```

### Time Components

Access individual components through `.dt` accessor:

```python
df["date"].dt.year
df["date"].dt.month
df["date"].dt.day
df["date"].dt.hour
df["date"].dt.dayofweek       # 0=Monday, 6=Sunday
df["date"].dt.is_month_end
df["date"].dt.to_period("M")  # convert to Period
```

## Generating Ranges (date_range)

```python
# Fixed frequency
idx = pd.date_range("2024-01-01", periods=10, freq="D")

# Start and end
idx = pd.date_range("2024-01-01", "2024-01-31", freq="D")

# Business days
idx = pd.date_range("2024-01-01", periods=10, freq="B")

# Hourly
idx = pd.date_range("2024-01-01", periods=24, freq="h")
```

### Common Frequencies

| alias | description |
|-------|-------------|
| `D` | Calendar day |
| `B` | Business day |
| `H` | Hour |
| `T`, `min` | Minute |
| `S` | Second |
| `W` | Weekly |
| `ME`, `M` | Month end |
| `MS`, `BM` | Month begin |
| `QE`, `Q` | Quarter end |
| `YE`, `Y` | Year end |

## Resampling

Convert time series to a different frequency. Group-by-like operation on time.

```python
# Downsample (high → low frequency)
daily = ts.resample("D").mean()
monthly = ts.resample("ME").sum()

# Upsample (low → high frequency)
hourly = daily.resample("h").interpolate("linear")
hourly = daily.resample("h").ffill()  # forward fill

# Multiple aggregations
result = ts.resample("D").agg(
    open="first",
    close="last",
    high="max",
    low="min",
    volume="sum",
)

# Rolling within resample
ts.resample("D").rolling(3).mean()
```

## Time Zone Handling

```python
# Localize naive timestamps
idx = pd.date_range("2024-01-01", periods=5, freq="D")
idx = idx.tz_localize("UTC")

# Convert between time zones
idx_utc = idx.tz_convert("America/New_York")

# Create with timezone
idx = pd.date_range("2024-01-01", periods=5, tz="US/Eastern")
```

## DateOffset Objects

Add/subtract calendar-aware offsets:

```python
# Basic offsets
ts + pd.DateOffset(days=5)
ts + pd.Timedelta(days=5)

# Calendar-aware (skips weekends for business days)
ts + pd.offsets.BusinessDay(5)
ts + pd.offsets.MonthEnd()       # next month end
ts + pd.offsets.BQuarterEnd()    # next business quarter end

# Custom business day with holidays
from pandas.tseries.holiday import USFederalHolidayCalendar
cbd = pd.offsets.CustomBusinessDay(calendar=USFederalHolidayCalendar())
ts + cbd * 5
```
