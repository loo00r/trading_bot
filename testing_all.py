import pandas as pd
import pandas_ta as ta
import numpy as np
import plotly.graph_objects as go

# Assuming your data is already loaded into df and cleaned
# Load CSV file, skip the header, and manually assign column names
df = pd.read_csv("coinbaseUSD_1-min_data.csv", names=["Unix Timestamp", "Date", "Symbol", "Open", "High", "Low", "Close", "Volume"])
df = df.drop(['Date', 'Symbol'], axis=1)
df.rename(columns={
    "Unix Timestamp":"timestamp",
    "Open":"open",
    "High":"high",
    "Low":"low",
    "Close":"close",
    "Volume":"volume"
}, inplace=True)

# Ensure the 'timestamp' column contains only numeric values
df = df[pd.to_numeric(df['timestamp'], errors='coerce').notnull()]

# Convert the Unix timestamp (milliseconds) to a human-readable datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'].astype(float), unit='ms')

# Set the new 'timestamp' column as the DataFrame index
df.set_index('timestamp', inplace=True)

# Ensure all numerical columns are in the correct format (float)
df['open'] = df['open'].astype(float)
df['high'] = df['high'].astype(float)
df['low'] = df['low'].astype(float)
df['close'] = df['close'].astype(float)
df['volume'] = df['volume'].astype(float)

# Filter rows where high != low
df = df[df['high'] != df['low']]

# Technical indicators
df["VWAP"] = ta.vwap(df.high, df.low, df.close, df.volume)
df['RSI'] = ta.rsi(df.close, length=16)
my_bbands = ta.bbands(df.close, length=14, std=2.0)
df = df.join(my_bbands)

# VWAP Signal generation
VWAPsignal = [0] * len(df)
backcandles = 15

for row in range(backcandles, len(df)):
    upt = 1
    dnt = 1
    for i in range(row-backcandles, row+1):
        if max(df.open[i], df.close[i]) >= df.VWAP[i]:
            dnt = 0
        if min(df.open[i], df.close[i]) <= df.VWAP[i]:
            upt = 0
    if upt == 1 and dnt == 1:
        VWAPsignal[row] = 3
    elif upt == 1:
        VWAPsignal[row] = 2
    elif dnt == 1:
        VWAPsignal[row] = 1

df['VWAPSignal'] = VWAPsignal

# TotalSignal function
def TotalSignal(l):
    if (df.VWAPSignal[l] == 2
        and df.close[l] <= df['BBL_14_2.0'][l]
        and df.RSI[l] < 45):
        return 2
    if (df.VWAPSignal[l] == 1
        and df.close[l] >= df['BBU_14_2.0'][l]
        and df.RSI[l] > 55):
        return 1
    return 0

# Applying the TotalSignal function
TotSignal = [0] * len(df)
for row in range(backcandles, len(df)):
    TotSignal[row] = TotalSignal(row)

df['TotalSignal'] = TotSignal

# pointposbreak function to mark signal points
def pointposbreak(x):
    if x['TotalSignal'] == 1:
        return x['high'] + 1e-4
    elif x['TotalSignal'] == 2:
        return x['low'] - 1e-4
    else:
        return np.nan

df['pointposbreak'] = df.apply(lambda row: pointposbreak(row), axis=1)

# Plot using Plotly
from datetime import datetime

dfpl = df
dfpl.reset_index(inplace=True)

# Candlestick and technical indicator plot
fig = go.Figure(data=[go.Candlestick(x=dfpl.index,
                open=dfpl['open'],
                high=dfpl['high'],
                low=dfpl['low'],
                close=dfpl['close']),
                go.Scatter(x=dfpl.index, y=dfpl.VWAP, 
                           line=dict(color='blue', width=1), 
                           name="VWAP"), 
                go.Scatter(x=dfpl.index, y=dfpl['BBL_14_2.0'], 
                           line=dict(color='green', width=1), 
                           name="BBL"),
                go.Scatter(x=dfpl.index, y=dfpl['BBU_14_2.0'], 
                           line=dict(color='green', width=1), 
                           name="BBU")])

# Add scatter plot for buy/sell signals
fig.add_scatter(x=dfpl.index, y=dfpl['pointposbreak'], mode="markers",
                marker=dict(size=10, color="MediumPurple"),
                name="Signal")

fig.show()
