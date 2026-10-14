import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 1. Set up the dashboard
st.title("2025 311 Service Request Dashboard")
st.write("Choose a date range to explore 311 service requests.")

# 2. Load the reduced dataset
DATA_FILE = "311_2025_dashboard.csv"

@st.cache_data
def load_data(file_path):
    data = pd.read_csv(file_path)
    data["request_date"] = pd.to_datetime(
        data["request_date"], errors="coerce"
    )
    data = data.dropna(subset=["request_date"])
    return data

try:
    df = load_data(DATA_FILE)
except FileNotFoundError:
    st.error(
        f"Could not find {DATA_FILE}. Place this CSV file in the same "
        "folder as app.py, then run the app again."
    )
    st.stop()
except KeyError:
    st.error("The CSV must contain a 'request_date' column.")
    st.stop()

if df.empty:
    st.warning("The dataset has no rows with valid request dates.")
    st.stop()

# 3. Replace START_DATE and END_DATE with date controls
min_date = df["request_date"].min().date()
max_date = df["request_date"].max().date()

date_columns = st.columns(2)
with date_columns[0]:
    start_date = st.date_input(
        "Start Date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
    )
with date_columns[1]:
    end_date = st.date_input(
        "End Date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
    )

if start_date > end_date:
    st.error("Start Date must be on or before End Date.")
    st.stop()

# 4. Filter first, then summarize and chart
# Add one day to the end date so the selected end date is included.
filtered_df = df[
    (df["request_date"] >= pd.Timestamp(start_date))
    & (
        df["request_date"]
        < pd.Timestamp(end_date) + pd.Timedelta(days=1)
    )
].copy()

st.write(f"Selected period: {start_date} through {end_date}")
st.metric("Requests in selected period", f"{len(filtered_df):,}")

if filtered_df.empty:
    st.info("No requests were found for this date range.")
    st.stop()

# 5. Chart 1: Top 10 Types of 311 Requests
st.subheader("Top 10 Types of 311 Requests")

if "service_name" not in filtered_df.columns:
    st.error("The CSV must contain a 'service_name' column for Chart 1.")
else:
    top_requests = (
        filtered_df["service_name"]
        .value_counts()
        .head(10)
        .sort_values()
    )

    fig1, ax1 = plt.subplots(figsize=(8, 5))
    top_requests.plot(kind="barh", ax=ax1)
    ax1.set_title("Top 10 Types of 311 Requests")
    ax1.set_xlabel("Number of Requests")
    ax1.set_ylabel("Service Type")
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

# 6. Chart 2: Requests Over Time
st.subheader("311 Requests Over Time")

requests_by_day = (
    filtered_df
    .groupby(filtered_df["request_date"].dt.date)
    .size()
)

fig2, ax2 = plt.subplots(figsize=(9, 4))
requests_by_day.plot(kind="line", ax=ax2)
ax2.set_title("311 Requests Over Time")
ax2.set_xlabel("Request Date")
ax2.set_ylabel("Number of Requests")
fig2.tight_layout()
st.pyplot(fig2)
plt.close(fig2)
