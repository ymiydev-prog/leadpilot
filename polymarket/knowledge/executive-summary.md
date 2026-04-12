# Polymarket Knowledge Base - Executive Summary

## 🎓 What I Learned

### 1. Documentation Structure

Polymarket has comprehensive documentation at docs.polymarket.com covering:

- **Concepts**: Markets/Events, Resolution, Prices/Orderbook, Positions/Tokens
- **Trading**: Overview, Quickstart, Orders, Fees, Gasless transactions, CTF tokens
- **API Reference**: CLOB API, Gamma API, Data API with TypeScript/Python/Rust SDKs
- **Market Makers**: Getting started, trading, inventory management, liquidity rewards

### 2. Three-Tier API Architecture

| API | Purpose | Authentication |
|-----|---------|----------------|
| **Gamma API** | Market metadata, events, historical data | None (public) |
| **Data API** | Analytics, price history, volume | None (public) |
| **CLOB API** | Trading operations, orders, cancellations | L1 (private key) → L2 (API credentials) |

### 3. Authentication Flow

```
L1 (Private Key)
    ↓ EIP-712 Signature
L2 API Credentials (Key + Secret + Passphrase)
    ↓ HMAC-SHA256
REST API Requests
```

**Signature Types**:
- `0` = EOA (standalone)
- `1` = POLY_PROXY (Magic Link)
- `2` = GNOSIS_SAFE (most common - browser wallets)

### 4. How Resolution Works

1. **Event occurs** → Market eligible for resolution
2. **Proposer posts bond** ($500-750 USDC.e)
3. **Challenge period** (2 hours)
4. **If no dispute** → Resolution confirmed
5. **If disputed** → New proposal OR DVM vote
6. **Winners** redeem tokens for $1 each

### 5. Fee Structure (March 2026)

- **Geopolitics**: FREE (0%)
- **Crypto**: Peak 1.80% at 50%
- **Finance/Politics/Tech**: Peak 1.00%
- **Sports**: Peak 0.75%
- **Economics**: Peak 1.50%

**Fees peak at 50% probability, decrease toward extremes**

### 6. Liquidity Rewards Program

- Daily USDC rewards for providing liquidity
- Must post orders within spread config (typically 3.5 cents)
- Minimum order size (typically 20 shares)
- Rewards based on formula considering spread, depth, and two-sided quoting

---

## 📊 Top Markets Analysis (March 2026)

### By Volume (Highest to Lowest)

| Rank | Market/Event | Volume | Liquidity | Spread | Category |
|------|---------------|--------|-----------|--------|----------|
| 1 | Democratic Presidential Nominee 2028 | $924M | $44.7M | Varies | Politics |
| 2 | Republican Presidential Nominee 2028 | $480M | $28.3M | Varies | Politics |
| 3 | Presidential Election Winner 2028 | $461M | $30.3M | Varies | Politics |
| 4 | 2026 FIFA World Cup Winner | $393M | $44.9M | 0.001 | Sports |
| 5 | 2026 NBA Champion | $205M | $10.2M | 0.01 | Sports |
| 6 | 2026 NHL Stanley Cup | $57M | $3.8M | 0.01 | Sports |
| 7 | Russia-Ukraine Ceasefire | $29M | $439K | Tight | Geopolitics |
| 8 | MicroStrategy sells Bitcoin | $22M | $243K | Tight | Crypto |
| 9 | GTA VI Events Bundle | $20M | $1.8M | 0.01 | Culture |
| 10 | Starmer out by...? | $10M | $180K | Tight | Politics |

---

## 🎯 5 Promising Markets for Small Accounts ($9.7 USDC)

### Market 1: Geopolitical - FREE Trading! 🌟

**Market**: "Russia-Ukraine Ceasefire before GTA VI?"
- **Volume**: $1.4M
- **Liquidity**: $99K
- **Spread**: 0.01 (1 cent)
- **Current Odds**: Yes 54.5%, No 45.5%
- **Category**: Geopolitics → **0% FEES**
- **End Date**: July 31, 2026

**Why Promising**:
- Zero fees = maximum capital efficiency
- Clear resolution criteria
- Active news flow
- Reasonable liquidity/spread

**Analysis**: Russian invasion news daily. Resolution criteria clear (official ceasefire agreement). 50-50 style odds mean good value on either side with news.

---

### Market 2: NBA Finals - High Liquidity 🏀

**Market**: "Oklahoma City Thunder win NBA Finals"
- **Volume**: $5.6M
- **Liquidity**: $307K
- **Spread**: 0.01 (1 cent)
- **Current Odds**: Yes 36.5%, No 63.5%
- **Category**: Sports (0.75% peak fee)
- **End Date**: ~June 2026

**Why Promising**:
- Excellent liquidity ($307K)
- Tight spread (1 cent)
- Regular news/analysis
- Statistical analysis possible

**Analysis**: OKC having strong season. Good for value betting on performance metrics and injury news.

---

### Market 3: FIFA World Cup - Tightest Spreads ⚽

**Market**: "Will [Team] win 2026 FIFA World Cup?" (Multiple options)
- **Volume**: $393M total event
- **Liquidity**: $1M+ per major team
- **Spread**: 0.001 (0.1 cent!) - TIGHTEST
- **Category**: Sports (0.75% peak fee)
- **End Date**: July 2026

**Top Teams to Consider**:
| Team | Odds | Liquidity |
|------|------|-----------|
| Argentina | 10% | $734K |
| Spain | 15.85% | $1.09M |
| France | 11% | $1.17M |
| England | 12.85% | $1.24M |

**Why Promising**:
- Extremely tight spreads (0.1 cent!)
- High volume = easy entry/exit
- Global expertise available
- Long runway for analysis

**Strategy**: Research teams, follow tournament news.

---

### Market 4: GTA VI Bundle - Cultural Phenomenon 🎮

**Market**: Various "Will X happen before GTA VI?"
- **Volume**: $20M total event
- **Liquidity**: $1.8M
- **Spread**: 0.01 (1 cent)
- **Category**: Culture (1.25% peak fee)
- **End Date**: July 31, 2026

**Sub-Markets**:
| Question | Yes Odds | Volume |
|----------|----------|--------|
| GTA VI before June 2026? | 2% | $12.9M |
| Jesus returns before GTA VI? | 48.5% | $10.3M |
| Bitcoin $1M before GTA VI? | 49% | $3.8M |

**Why Promising**:
- Confirmed Fall 2026 release (not before June = good bet on No)
- Viral marketing potential
- Clear resolution criteria

**Strategy**: "GTA VI before June 2026?" at 2% Yes → bet No for near-certain return. But spread wide on low prob.

---

### Market 5: 2028 Democratic Primary - Massive Volume 🇺🇸

**Market**: Various Democratic presidential nominee candidates
- **Volume**: $924M total event
- **Liquidity**: $44.7M
- **Spread**: 0.001-0.002 (tightest!)
- **Category**: Politics (1% peak fee)
- **End Date**: 2028 (long term)

**Interesting Sub-Markets**:
| Candidate | Yes Odds | Volume |
|-----------|----------|--------|
| Stephen A. Smith | 1% | $13.5M |
| Oprah Winfrey | 1.4% | $42.6M |
| Gretchen Whitmer | 1.5% | $7M |

**Why Promising**:
- Extremely tight spreads
- Massive liquidity
- Long-term position with news catalysts
- Polls provide data edge

**Strategy**: Follow polling/news. Low-probability candidates can spike on announcements.

---

## 💰 Recommended Strategy: $9.7 USDC

### Approach: Single Focus on Fee-Free Market

Given small capital, I recommend **concentrating on one geopolitical market** for maximum efficiency:

### Primary Recommendation:

**Market**: "Russia-Ukraine Ceasefire before GTA VI?"

**Position**: 
- Bet **Yes** around 54-55% OR **No** around 45-46%
- Depends on current news analysis

**Why This Strategy**:
1. **Zero fees** = 100% of capital works for you
2. **Reasonable spread** (1 cent) = minimal slippage
3. **Clear resolution** = defined outcome
4. **Active news** = opportunities for value trades
5. **Good liquidity** ($99K) = ability to exit

**Execution**:
```
Capital: $9.70
Spread after entry: ~$9.60 effective position
If odds move from 54% to 64%: +100% → $19.20 profit potential
If resolution in favor: +$8.70 (win at 54¢ redeems at $1)
```

### Alternative: Market Making Approach

If you want passive income rather than directional betting:

**Market**: FIFA World Cup (tightest spreads)
**Strategy**: Post bids/asks around fair value
**Expected Return**: Spread capture + maker rebates

**Example**:
```
Market: Spain wins @ 15.85%
Post bid @ 15.75¢, ask @ 15.95¢
Capture 0.2¢ spread per fill
Plus daily maker rebates (25% of taker fees)
```

**Issue**: $9.7 may not meet minimum order size (usually 5-20 shares)

---

## ⚠️ Important Considerations

### Capital Limitations:
- **Minimum order**: Typically5 shares (check `orderMinSize`)
- **Fees**: Even small fees eat into small capital
- **Spread costs**: Must overcome spread to profit

### Recommended Minimum:
- Directional bets: $10 minimum meaningful position
- Market making: $100+ to meet multiple order requirements

### With $9.7 specifically:
1. **Focus on fee-free markets** (Geopolitics)
2. **Choose tightest spreads** (minimize slippage)
3. **Single position** (no diversification at this level)
4. **High confidence thesis** required

---

## 📁 Knowledge Files Created

1. **strategies.md**: Complete trading strategies guide
   - Value betting
   - Market making
   - Arbitrage
   - News trading
   - Resolution betting
   - Fee structure details
   - Technical implementation

2. **markets-guide.md**: Market navigation reference
   - Platform overview
   - Market categories
   - Top markets by volume/liquidity
   - Market selection criteria
   - API endpoints
   - Resolution rules

---

## 🔗 Key Links

- **Documentation**: https://docs.polymarket.com/
- **Gamma API**: https://gamma-api.polymarket.com
- **CLOB API**: https://clob.polymarket.com
- **UMA Oracle**: https://oracle.uma.xyz/
- **Discord**: https://discord.com/invite/polymarket

---

*Generated: 2026-03-28*
*Agent: Poly - Polymarket Expert Study*