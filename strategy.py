import pandas as pd

# === CONFIGURATION ===
TARGET_COIN = "LDO"
TIMEFRAME = "4H"

ANCHORS = [
    {
        "symbol": "ETH",
        "timeframe": "4H",
        "lag": 1
    }
]

BUY_RULES = [
    {
        "symbol": "ETH",
        "timeframe": "4H",
        "lag": 1,
        "change_pct": 2.0,
        "direction": "up"
    },
    {
        "symbol": "LDO",
        "timeframe": "4H",
        "lag": 0,
        "change_pct": 1.0,
        "direction": "up"
    }
]

SELL_RULES = [
    {
        "symbol": "ETH",
        "timeframe": "4H",
        "lag": 0,
        "change_pct": -2.0,
        "direction": "down"
    }
]

# === STRATEGY ENGINE ===
def generate_signals(candles_target: pd.DataFrame, candles_anchor: pd.DataFrame) -> pd.DataFrame:
    try:
        df = candles_target[['timestamp']].copy()
        for anchor in ANCHORS:
            col = f"close_{anchor['symbol']}"
            if col not in candles_anchor.columns:
                raise ValueError(f"Missing column: {col}")
            df[col] = candles_anchor[col].values

        signals = []
        for i in range(len(df)):
            buy_pass = True
            sell_pass = False

            for rule in BUY_RULES:
                col = f"close_{rule['symbol']}"
                if col not in df.columns or pd.isna(df[col].iloc[i]):
                    buy_pass = False
                    break
                change = df[col].pct_change().shift(rule['lag']).iloc[i]
                if pd.isna(change):
                    buy_pass = False
                    break
                if rule['direction'] == 'up' and change <= rule['change_pct'] / 100:
                    buy_pass = False
                    break
                if rule['direction'] == 'down' and change >= rule['change_pct'] / 100:
                    buy_pass = False
                    break

            for rule in SELL_RULES:
                col = f"close_{rule['symbol']}"
                if col not in df.columns or pd.isna(df[col].iloc[i]):
                    continue
                change = df[col].pct_change().shift(rule['lag']).iloc[i]
                if pd.isna(change):
                    continue
                if rule['direction'] == 'down' and change <= rule['change_pct'] / 100:
                    sell_pass = True
                if rule['direction'] == 'up' and change >= rule['change_pct'] / 100:
                    sell_pass = True

            if buy_pass:
                signals.append("BUY")
            elif sell_pass:
                signals.append("SELL")
            else:
                signals.append("HOLD")

        df['signal'] = signals
        return df[['timestamp', 'signal']]

    except Exception as e:
        raise RuntimeError(f"Strategy failed: {e}")

def get_coin_metadata() -> dict:
    return {
        "target": {"symbol": TARGET_COIN, "timeframe": TIMEFRAME},
        "anchors": [{"symbol": a["symbol"], "timeframe": a["timeframe"]} for a in ANCHORS]
    }
