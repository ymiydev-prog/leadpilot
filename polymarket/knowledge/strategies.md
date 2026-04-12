# Polymarket Trading Strategies

## 📚 Core Concepts Learned

### Market Mechanics
- **Prices = Probabilities**: Share prices range $0.00-$1.00, directly representing market's probability estimate
- **Binary Markets**: Yes/No outcomes. Winning tokens redeem for $1, losing tokens = $0
- **Negative Risk Markets**: Multi-outcome events where only one outcome wins. A "No" on one outcome converts to "Yes" on all others
- **Order Book (CLOB)**: Hybrid decentralized - offchain matching, onchain settlement. Non-custodial.

### Three API Types
1. **Gamma API**: Market metadata, events, historical data (public, read-only)
2. **Data API**: Analytics, price history, volume data (public, read-only)
3. **CLOB API**: Trading operations - orders, cancellations, balances (requires L1/L2 auth)

### Authentication Model
- **L1 (Private Key)**: EIP-712 signature to create/derive API credentials
- **L2 (API Key)**: HMAC-SHA256 for all trading operations
- **Signature Types**:
  - `0` = EOA (standalone wallet, pays own gas)
  - `1` = POLY_PROXY (Magic Link accounts, requires exported PK)
  - `2` = GNOSIS_SAFE (most common - MetaMask/Rabby browser wallets)

---

## 🎯 Trading Strategies

### 1. Value Betting (Finding Mispriced Markets)

**Concept**: Find markets where your estimated probability differs significantly from market price.

**Process**:
1. Research the event thoroughly
2. Estimate your own probability (with confidence interval)
3. Compare to market implied probability
4. Bet when: `|your_prob - market_prob| > edge_threshold`

**Edge Thresholds**:
- Low confidence: 15%+ edge
- Medium confidence: 10%+ edge
- High confidence: 5%+ edge

**Example**:
- Market: "Team X wins championship" at 25¢ (25% implied)
- Your analysis: 40% probability
- Edge: 15% → BUY at up to 40¢

**Risk Management**:
- Never bet >5-10% of bankroll on single market
- Consider resolution time (capital efficiency)
- Check liquidity/spread for exit options

---

### 2. Market Making (Providing Liquidity)

**Concept**: Post both bid and ask orders around a fair value, earning the spread.

**Rewards**:
- Liquidity Rewards Program: Daily USDC for providing tight two-sided quotes
- Maker Rebates: 20-50% of taker fees redistributed (category dependent)

**Best Practices**:
```python
# Two-sided quoting example
fair_value = 0.50
spread = 0.02  # 2 cents

bid_price = fair_value - spread/2  # 0.49
ask_price = fair_value + spread/2  # 0.51

# Post both sides
client.createAndPostOrder(tokenID, Side.BUY, bid_price, size)
client.createAndPostOrder(tokenID, Side.SELL, ask_price, size)
```

**Key Parameters**:
- Max spread config: Markets have `rewardsMaxSpread` (typically 3.5 cents)
- Min size config: `rewardsMinSize` for rewards eligibility
- Tick size: Prices must match market's tick (0.1, 0.01, 0.001, or 0.0001)

**Risk Management**:
- **Inventory skew**: Adjust quotes based on position to encourage balancing fills
- **Price guards**: Validate prices vs book midpoint before posting
- **Kill switch**: Use `cancelAll()` on errors or position breaches
- **GTD orders**: Auto-expire before known events

---

### 3. Arbitrage (Cross-Platform/Market)

**Types**:

**A. Cross-Platform Arbitrage**
- Same event on Polymarket vs. other prediction markets (Kalshi, PredictIt)
- Exploit price differences (account for fees/spread)

**B. Cross-Market Arbitrage**
- Related markets with correlated outcomes
- Example: "Candidate X wins primary" and "Candidate X becomes nominee"
- Mathematical relationships between probabilities

**C. Negative Risk Arbitrage**
- In multi-outcome events, buying "No" on all outcomes is mathematically equivalent to... nothing useful
- BUT: Converting between outcomes via Neg Risk Adapter can create opportunities

**Example - Cross-Platform**:
```
Polymarket: "Event X happens" = 45¢
Kalshi: Same event = 55¢

Arbitrage:
- Buy Yes on Polymarket at 45¢
- Sell/No on Kalshi at 55¢
- Guaranteed profit (minus fees/spreads)
```

**Risk**: Platform fees, withdrawal times, resolution differences

---

### 4. News Trading (Event-Driven)

**Concept**: React quickly to news that affects market probabilities.

**Setup**:
- Monitor news feeds, Twitter/X, official announcements
- Set up alerts for relevant keywords
- Use WebSocket for real-time orderbook data

**Execution**:
```python
# Subscribe to real-time updates
ws_client.subscribe([{"token_ids": [token_id], "channel": "user"}])
```

**Timing Windows**:
- Pre-announcement: Positioning based on expected outcomes
- Post-announcement: Fastest reaction to unexpected news
- Resolution: Betting on disputed markets (requires UMA bond)

**Risk**:
- News interpretation errors
- Market already priced in
- Competing with bots (latency matters)

---

### 5. Resolution Betting (Post-Event)

**Concept**: After an event occurs but before resolution, bet on the outcome.

**UMA Resolution Process**:
1. Anyone can propose outcome (requires $750 USDC.e bond)
2. 2-hour challenge period for disputes
3. If disputed: New proposal OR escalate to DVM vote (48 hours)
4. Winners: Bond + half of loser's bond

**Strategy Types**:

**A. Early Resolution**
- If outcome is clear, propose quickly for reward
- Risk: Wrong proposal = lose bond

**B. Dispute Resolution**
- Spot incorrect proposals during challenge period
- Dispute with correct outcome
- Win: Get bond + half of proposer's bond

**C. Resolution Betting**
- Bet on outcomes after event but before resolution
- Market price may lag actual outcome

---

## 💰 Fee Structure (March 2026)

### Taker Fees (by category)
| Category | Fee Rate | Exponent | Peak Effective Rate |
|----------|----------|----------|---------------------|
| Crypto | 0.072 | 1 | 1.80% |
| Sports | 0.03 | 1 | 0.75% |
| Finance | 0.04 | 1 | 1.00% |
| Politics | 0.04 | 1 | 1.00% |
| Economics | 0.03 | 0.5 | 1.50% |
| Culture | 0.05 | 1 | 1.25% |
| Weather | 0.025 | 0.5 | 1.25% |
| Tech | 0.04 | 1 | 1.00% |
| Mentions | 0.25 | 2 | 1.56% |
| Other | 0.2 | 2 | 1.25% |
| **Geopolitics** | **0** | - | **0% (FREE)** |

### Fee Formula
```
fee = C × p × feeRate × (p × (1-p))^exponent
```
- C = shares traded
- p = price
- Fee peaks at 50% probability, decreases toward extremes

### Maker Rebates
| Category | Rebate % | Distribution |
|----------|----------|--------------|
| Crypto | 20% | Fee-curve weighted |
| Sports | 25% | Fee-curve weighted |
| Finance | 50% | Fee-curve weighted |
| Politics | 25% | Fee-curve weighted |

---

## 🛠️ Technical Implementation

### SDK Setup
```python
from py_clob_client.client import ClobClient
import os

client = ClobClient(
    host="https://clob.polymarket.com",
    chain_id=137,  # Polygon
    key=os.getenv("PRIVATE_KEY"),
    creds=api_creds,
    signature_type=2,  # GNOSIS_SAFE
    funder="0x..."  # Your proxy wallet address
)
```

### Order Types
- **GTC**: Good-til-cancelled (default, passive quoting)
- **GTD**: Good-til-date (auto-expire)
- **FOK**: Fill-or-kill (all or nothing, aggressive)
- **FAK**: Fill-and-kill (partial ok, aggressive)

### Key Endpoints
```python
# Get market data
tick_size = client.get_tick_size(token_id)

# Place order
order = client.create_and_post_order(
    OrderArgs(
        token_id=token_id,
        side=BUY,  # or SELL
        price=0.55,
        size=100,
    ),{
        "tick_size": "0.01",
        "neg_risk": False,  # True for multi-outcome events
    },order_type=OrderType.GTC
)

# Cancel
client.cancel(order_id=order_id)
client.cancel_all()
```

---

## 📊 Market Analysis Checklist

### Before Trading Any Market:

1. **Liquidity Check**:
   - Spread <= reward spread config (typically 3.5¢)?
   - Sufficient depth at price levels?
   - Volume/24h meaningful?

2. **Resolution Rules**:
   - Read full resolution criteria
   - Check resolution source
   - Note end date and any special conditions

3. **Fee Category**:
   - Is market fee-enabled? (Geometry = FREE)
   - What's the category's peak fee?

4. **Neg Risk**:
   - Is it a multi-outcome event?
   - Set `neg_risk=True` in order options

5. **Market Health**:
   - `competitive` score (liquidity quality)
   - `acceptingOrders` flag
   - `closed` / `resolved` status

---

## ⚠️ Risk Management Rules

1. **Position Sizing**:
   - Single position: max 10% of bankroll
   - Concentrated theme: max 25% of bankroll

2. **Spread Discipline**:
   - Never buy if spread >3% (unless very high confidence)
   - Limit orders > market orders for better fills

3. **Exit Planning**:
   - Always have exit plan before entering
   - Check orderbook depth for potential slippage

4. **Resolution Time**:
   - Longer resolution = lower capital efficiency
   - Consider opportunity cost

5. **Platform Risk**:
   - Smart contract risk (Polymarket is non-custodial)
   - UMA Oracle disputes can take 4-6 days

---

## 🔗 Resources

- **Gamma API**: `https://gamma-api.polymarket.com`
- **CLOB API**: `https://clob.polymarket.com`
- **WebSocket**: Real-time orderbook updates
- **UMA Oracle Portal**: `https://oracle.uma.xyz/`
- **Polymarket Discord**: Resolution discussions

---

*Last Updated: 2026-03-28*
*Documentation Source: https://docs.polymarket.com/*