#!/usr/bin/env python3
"""
Poly - Polymarket Trading Agent
Execute: Buy NO on Russia-Ukraine Ceasefire before GTA VI @ 45-46 cents
Capital: $9.70 USDC (full position)
"""

import os
import sys
import json
from decimal import Decimal
from datetime import datetime

# Add venv to path
sys.path.insert(0, '/root/.openclaw/workspace/polymarket/venv/lib/python3.12/site-packages')

from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON
from py_clob_client.clob_types import OrderArgs, OrderType

# Credentials
PRIVATE_KEY = "ea86d5d3b47f053cedab4905c056991a2f16ac1eb66ba3a139fff11d900d75fc"
WALLET_ADDRESS = "0xDcE71FFa4A4fDCf8B3EC7D116A8eB8f2Ed1A5D5B"
SIGNATURE_TYPE = 2  # GNOSIS_SAFE
PROXY_ADDRESS = "0xc6052F3EE2e98055d07D2B6005BE1E9888914d4F"

# Market target
MARKET_QUERY = "Russia-Ukraine Ceasefire before GTA VI"
TARGET_SIDE = "NO"
TARGET_PRICE_MIN = Decimal("0.45")
TARGET_PRICE_MAX = Decimal("0.46")
POSITION_SIZE = Decimal("9.70")  # $9.70 USDC

def log(msg, level="INFO"):
    timestamp = datetime.utcnow().isoformat()
    print(f"[{timestamp}] [{level}] {msg}")
    sys.stdout.flush()

def main():
    log("=" *60)
    log("POLY - Polymarket Trading Agent")
    log("=" *60)
    
    # Step 1: Initialize client with POLY_PROXY signature type
    log("Step 1: Initializing CLOB client with POLY_PROXY auth...")
    
    # First, create L1 client to derive credentials
    l1_client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137,  # Polygon
        key=PRIVATE_KEY,
        signature_type=SIGNATURE_TYPE,
        funder=PROXY_ADDRESS,  # Proxy wallet for GNOSIS_SAFE
    )
    
    # Derive API credentials
    log("Deriving API credentials from private key...")
    try:
        api_creds = l1_client.create_or_derive_api_creds()
        log(f"API Key: {api_creds.api_key[:20]}...")
        log(f"API Secret: {api_creds.api_secret[:10]}...")
        log(f"API Passphrase: {api_creds.api_passphrase[:10]}...")
        log("Credentials derived successfully!")
    except Exception as e:
        log(f"ERROR deriving credentials: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return
    
    # Now create L2 client with credentials
    log("\nCreating L2 authenticated client...")
    client = ClobClient(
        host="https://clob.polymarket.com",
        chain_id=137,  # Polygon
        key=PRIVATE_KEY,
        creds=api_creds,
        signature_type=SIGNATURE_TYPE,
        funder=PROXY_ADDRESS,  # Proxy wallet for GNOSIS_SAFE
    )
    log(f"Client mode: L2 (Authenticated for trading)")
    
    # Step 2: Get USDC balance
    log("\nStep 2: Checking USDC balance...")
    try:
        # Get balance for collateral asset
        # USDC on Polygon: 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174
        USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        
        # Try getting balance via client
        balance_info = client.get_balance_allowance()
        log(f"Balance info: {balance_info}")
    except Exception as e:
        log(f"Note: Balance check returned: {e}")
    
    # Step 3: Search for the market
    log("\nStep 3: Searching for market...")
    log(f"Query: '{MARKET_QUERY}'")
    
    try:
        # Use Gamma API to find the market
        import requests
        
        gamma_url = "https://gamma-api.polymarket.com/markets"
        params = {
            "active": "true",
            "closed": "false",
            "limit": 100
        }
        
        response = requests.get(gamma_url, params=params)
        markets = response.json()
        
        target_market = None
        for market in markets:
            if "russia" in market.get("question", "").lower() and "ukraine" in market.get("question", "").lower() and "ceasefire" in market.get("question", "").lower():
                if "gta" in market.get("question", "").lower() or "GTA" in market.get("question", ""):
                    target_market = market
                    break
        
        if not target_market:
            # Try slug-based search
            search_url = f"https://gamma-api.polymarket.com/markets?slug=russia-ukraine-ceasefire-before-gta-vi"
            response = requests.get(search_url)
            markets = response.json()
            if markets:
                target_market = markets[0]
        
        if not target_market:
            log("ERROR: Could not find the target market!", "ERROR")
            return
        
        log(f"Found market: {target_market.get('question')}")
        log(f"Market ID: {target_market.get('condition_id')}")
        
        # Get token IDs
        clob_token_ids = target_market.get("clobTokenIds", [])
        if isinstance(clob_token_ids, str):
            clob_token_ids = json.loads(clob_token_ids)
        
        log(f"Token IDs: {clob_token_ids}")
        
        # For binary markets: token_ids[0] = YES, token_ids[1] = NO
        # But we need to verify which is which
        outcomes = target_market.get("outcomes", [])
        if isinstance(outcomes, str):
            outcomes = json.loads(outcomes)
        
        log(f"Outcomes: {outcomes}")
        
        # Find NO token
        no_token_id = None
        if len(outcomes) >= 2:
            # outcomes[0] is usually "Yes", outcomes[1] is "No"
            for i, outcome in enumerate(outcomes):
                if outcome.lower() == "no":
                    no_token_id = clob_token_ids[i]
                    break
        
        if not no_token_id and len(clob_token_ids) >= 2:
            # Assume standard order: [Yes, No]
            no_token_id = clob_token_ids[1]
        
        log(f"NO Token ID: {no_token_id}")
        
        # Get current market prices
        outcome_prices = target_market.get("outcomePrices", "[]")
        if isinstance(outcome_prices, str):
            outcome_prices = json.loads(outcome_prices)
        
        log(f"Current prices - YES: {outcome_prices[0] if len(outcome_prices) > 0 else 'N/A'}, NO: {outcome_prices[1] if len(outcome_prices) > 1 else 'N/A'}")
        
        # Step 4: Get tick size for the token
        log("\nStep 4: Getting tick size...")
        try:
            tick_size = client.get_tick_size(no_token_id)
            log(f"Tick size: {tick_size}")
        except Exception as e:
            log(f"Tick size request returned: {e}")
            tick_size = "0.01"  # Default for most markets
        
        # Step 5: Get order book
        log("\nStep 5: Getting order book...")
        try:
            orderbook = client.get_order_book(no_token_id)
            log(f"Orderbook retrieved")
            
            # Get best prices
            if orderbook.get("bids"):
                best_bid = orderbook["bids"][0]["price"]
                log(f"Best BID: {best_bid}")
            if orderbook.get("asks"):
                best_ask = orderbook["asks"][0]["price"]
                log(f"Best ASK: {best_ask}")
        except Exception as e:
            log(f"Orderbook request: {e}")
        
        # Step 6: Place the order
        log("\n" + "=" *60)
        log("Step 6: PLACING ORDER")
        log("=" *60)
        
        # Calculate price (use middle of target range)
        price = (TARGET_PRICE_MIN + TARGET_PRICE_MAX) / 2
        
        # Calculate size in shares (for buying, size = amount / price)
        # For $9.70 at 45.5 cents each, we get ~21.3 shares
        size = POSITION_SIZE / price
        
        log(f"Order parameters:")
        log(f"  Token ID: {no_token_id}")
        log(f"  Side: BUY (comprar NO)")
        log(f"  Price: ${price:.4f} ({float(price)*100:.2f} cents)")
        log(f"  Size: {size:.2f} shares")
        log(f"  Total cost: ${float(price) * float(size):.2f} USDC")
        log(f"  Order type: GTC (Good Till Cancel)")
        
        # Create the order
        try:
            order_args = OrderArgs(
                token_id=no_token_id,
                side="BUY",  # Comprar NO
                price=float(price),
                size=float(size),
            )
            
            # Get neg_risk flag from market
            neg_risk = target_market.get("neg_risk", False)
            if isinstance(neg_risk, str):
                neg_risk = neg_risk.lower() == "true"
            
            log(f"Negative risk market: {neg_risk}")
            
            # Create and post order
            log("\nPosting order to Polymarket CLOB...")
            
            from py_clob_client.clob_types import CreateOrderOptions
            
            order_options = CreateOrderOptions(
                tick_size=tick_size,
                neg_risk=neg_risk
            )
            
            order_response = client.create_and_post_order(
                order_args,
                order_options
            )
            
            log("\n" + "=" *60)
            log("ORDER PLACED SUCCESSFULLY!")
            log("=" *60)
            log(f"Order response: {json.dumps(order_response, indent=2) if isinstance(order_response, dict) else order_response}")
            
            # Save order details
            order_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "market": target_market.get("question"),
                "market_id": target_market.get("condition_id"),
                "token_id": no_token_id,
                "side": "BUY",
                "outcome": "NO",
                "price": str(price),
                "size": str(size),
                "total_usdc": str(float(price) * float(size)),
                "order_response": order_response if isinstance(order_response, dict) else str(order_response)
            }
            
            with open("/root/.openclaw/workspace/polymarket/logs/orders.json", "a") as f:
                f.write(json.dumps(order_log) + "\n")
            
            log("\nOrder logged to /root/.openclaw/workspace/polymarket/logs/orders.json")
            
        except Exception as e:
            log(f"ERROR placing order: {e}", "ERROR")
            import traceback
            log(traceback.format_exc(), "ERROR")
            return
        
    except Exception as e:
        log(f"ERROR in market search: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return
    
    log("\n" + "=" *60)
    log("OPERATION COMPLETE")
    log("=" *60)

if __name__ == "__main__":
    main()