
import frappe
from frappe import _
from wallet_engine.wallet_engine.balance import get_running_balance, sum_balance

def validate_wallet_balance(doc, method=None):
    if not doc.get('wallet_sale'):
        return

    # amount to check: outstanding if draft, else grand_total
    amount_to_check = float(doc.grand_total or 0)
    bal = get_running_balance('Customer', doc.customer)
    if bal is None:
        bal = sum_balance('Customer', doc.customer)

    if bal < amount_to_check:
        frappe.throw(_("Insufficient wallet balance. Available: {0}, Required: {1}")
                     .format(frappe.utils.fmt_money(bal), frappe.utils.fmt_money(amount_to_check)))

def on_submit_insert_consumption(doc, method=None):
    if not doc.get('wallet_sale'):
        return

    amount = float(doc.rounded_total or doc.grand_total or 0)
    wt = frappe.get_doc({
        'doctype': 'Wallet Transaction',
        'posting_date': doc.posting_date or frappe.utils.nowdate(),
        'party_type': 'Customer',
        'party': doc.customer,
        'transaction_type': 'Consumption',
        'amount': amount,
        'reference_doctype': 'Sales Invoice',
        'reference_name': doc.name,
        'remarks': 'Wallet consumption on Sales Invoice'
    })
    wt.insert(ignore_permissions=True)

def on_cancel_reverse_consumption(doc, method=None):
    # Insert a reversing 'Top-Up' equivalent for the canceled consumption OR mark a cancel reference
    # Simpler: insert an Adjustment to credit back
    amount = float(doc.rounded_total or doc.grand_total or 0)
    if amount <= 0 or not doc.get('wallet_sale'):
        return

    wt = frappe.get_doc({
        'doctype': 'Wallet Transaction',
        'posting_date': frappe.utils.nowdate(),
        'party_type': 'Customer',
        'party': doc.customer,
        'transaction_type': 'Transfer In',  # reverse effect (credit back)
        'amount': amount,
        'reference_doctype': 'Sales Invoice',
        'reference_name': doc.name,
        'remarks': 'Reversal of wallet consumption due to Sales Invoice cancel'
    })
    wt.insert(ignore_permissions=True)
