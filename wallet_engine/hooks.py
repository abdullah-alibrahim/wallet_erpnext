
app_name = "wallet_engine"
app_title = "Wallet Engine"
app_publisher = "Abdullah "
app_description = "ERPNext Wallet Engine"
app_email = "noreply@example.com"
app_license = "MIT"

# Include client scripts
app_include_js = ["public/js/sales_invoice_wallet.js"]

# Document event hooks
doc_events = {
    "Sales Invoice": {
        "validate": "wallet_engine.events.sales_invoice.validate_wallet_balance",
        "on_submit": "wallet_engine.events.sales_invoice.on_submit_insert_consumption",
        "on_cancel": "wallet_engine.events.sales_invoice.on_cancel_reverse_consumption"
    },
    "Journal Entry": {
        "on_submit": "wallet_engine.events.journal_entry.on_submit_insert_topup",
        "on_cancel": "wallet_engine.events.journal_entry.on_cancel_reverse_topup"
    },
    "Wallet Transfer": {
        "on_submit": "wallet_engine.wallet_engine.doctype.wallet_transfer.wallet_transfer.on_submit",
        "on_cancel": "wallet_engine.wallet_engine.doctype.wallet_transfer.wallet_transfer.on_cancel"
    },
    "Wallet Transaction": {
        "after_insert": "wallet_engine.events.wallet_transaction.after_insert_update_running_balance",
        "on_cancel": "wallet_engine.events.wallet_transaction.on_cancel_recompute_running_balance"
    }
}

# Whitelisted methods
# (they live in wallet_engine/wallet_engine/api.py)
api_methods = [
    "wallet_engine.wallet_engine.api.wallet_balance",
    "wallet_engine.wallet_engine.api.wallet_transfer",
    "wallet_engine.wallet_engine.api.wallet_topup_via_journal_entry",
    "wallet_engine.wallet_engine.api.wallet_transactions"
]
