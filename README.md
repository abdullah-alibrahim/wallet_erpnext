
# ERPNext Wallet Engine

Production-grade wallet module for ERPNext:

- Wallet Transaction (Top-Up, Consumption, Transfer In/Out, Reservation)
- Wallet Transfer (double-entry wallet move)
- Wallet Reservation (webshop holds)
- Sales Invoice client script for Wallet Sale toggle
- REST API endpoints for balance, transfer, top-up
- Running balance caching for fast reads
- Hooks for validation/enforcement

## Install (development)

1) Copy this folder into your bench apps directory:
```
bench/apps/wallet_engine
```
or install from path:
```
bench get-app wallet_engine /path/to/wallet_engine
```

2) Install into a site:
```
bench --site your.site install-app wallet_engine
bench --site your.site migrate
```

3) Ensure you have a Receivable account named "Wallet Balance - COMPANYABBR".
