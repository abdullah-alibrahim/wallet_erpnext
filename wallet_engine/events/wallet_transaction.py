
import frappe

def _compute_balance_delta(transaction_type, amount):
    if transaction_type in ('Top-Up','Transfer In','Reservation Release'):
        return float(amount)
    if transaction_type in ('Consumption','Transfer Out','Reservation'):
        return -float(amount)
    if transaction_type == 'Adjustment':
        return float(amount)
    return 0.0

def after_insert_update_running_balance(doc, method=None):
    # Update running_balance for the inserted record, based on last known balance
    last = frappe.db.sql('''
        SELECT running_balance FROM `tabWallet Transaction`
        WHERE name != %s AND party_type=%s AND party=%s
        ORDER BY posting_date DESC, creation DESC
        LIMIT 1
    ''', (doc.name, doc.party_type, doc.party))
    last_bal = float(last[0][0]) if last else 0.0
    delta = _compute_balance_delta(doc.transaction_type, doc.amount)
    new_bal = last_bal + delta
    frappe.db.set_value('Wallet Transaction', doc.name, 'running_balance', new_bal, update_modified=False)

def on_cancel_recompute_running_balance(doc, method=None):
    # For simplicity we won't delete; in production you may add a canceled flag and recompute
    pass
