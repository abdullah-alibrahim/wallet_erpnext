
import frappe
from frappe import _

def on_submit(doc, method=None):
    # Validate balance
    sender_bal = frappe.db.sql('''
        SELECT running_balance FROM `tabWallet Transaction`
        WHERE party_type=%s AND party=%s
        ORDER BY posting_date DESC, creation DESC
        LIMIT 1
    ''', (doc.from_party_type, doc.from_party))
    bal = float(sender_bal[0][0]) if sender_bal else 0.0
    if bal < float(doc.amount or 0):
        frappe.throw(_("Insufficient balance to transfer."))

    # Transfer Out (sender)
    frappe.get_doc({
        'doctype': 'Wallet Transaction',
        'posting_date': frappe.utils.nowdate(),
        'party_type': doc.from_party_type,
        'party': doc.from_party,
        'transaction_type': 'Transfer Out',
        'amount': float(doc.amount),
        'reference_doctype': 'Wallet Transfer',
        'reference_name': doc.name,
        'target_party_type': doc.to_party_type,
        'target_party': doc.to_party,
        'remarks': doc.remarks or ''
    }).insert(ignore_permissions=True)

    # Transfer In (receiver)
    frappe.get_doc({
        'doctype': 'Wallet Transaction',
        'posting_date': frappe.utils.nowdate(),
        'party_type': doc.to_party_type,
        'party': doc.to_party,
        'transaction_type': 'Transfer In',
        'amount': float(doc.amount),
        'reference_doctype': 'Wallet Transfer',
        'reference_name': doc.name,
        'target_party_type': doc.from_party_type,
        'target_party': doc.from_party,
        'remarks': doc.remarks or ''
    }).insert(ignore_permissions=True)

def on_cancel(doc, method=None):
    # simple reversal entries
    frappe.get_doc({
        'doctype': 'Wallet Transaction',
        'posting_date': frappe.utils.nowdate(),
        'party_type': doc.from_party_type,
        'party': doc.from_party,
        'transaction_type': 'Transfer In',
        'amount': float(doc.amount),
        'reference_doctype': 'Wallet Transfer',
        'reference_name': doc.name,
        'remarks': 'Reverse transfer (cancel)'
    }).insert(ignore_permissions=True)

    frappe.get_doc({
        'doctype': 'Wallet Transaction',
        'posting_date': frappe.utils.nowdate(),
        'party_type': doc.to_party_type,
        'party': doc.to_party,
        'transaction_type': 'Transfer Out',
        'amount': float(doc.amount),
        'reference_doctype': 'Wallet Transfer',
        'reference_name': doc.name,
        'remarks': 'Reverse transfer (cancel)'
    }).insert(ignore_permissions=True)
