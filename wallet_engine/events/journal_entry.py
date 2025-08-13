
import frappe
from frappe import _

def on_submit_insert_topup(doc, method=None):
    # detect top-up by presence of Debit to Debtors (with party) and Credit to Wallet Balance
    company = doc.company
    accounts = doc.accounts or []
    wallet_account = _get_wallet_account(company)

    # find any credit to wallet and debit to debtors with party
    credit_wallet = any(a.account == wallet_account and float(a.credit_in_account_currency or 0) > 0 for a in accounts)
    for a in accounts:
        if a.party_type == 'Customer' and float(a.debit_in_account_currency or 0) > 0 and credit_wallet:
            amount = float(a.debit_in_account_currency)
            wt = frappe.get_doc({
                'doctype': 'Wallet Transaction',
                'posting_date': doc.posting_date or frappe.utils.nowdate(),
                'party_type': 'Customer',
                'party': a.party,
                'transaction_type': 'Top-Up',
                'amount': amount,
                'reference_doctype': 'Journal Entry',
                'reference_name': doc.name,
                'remarks': 'Wallet Top-Up via Journal Entry'
            })
            wt.insert(ignore_permissions=True)

def on_cancel_reverse_topup(doc, method=None):
    company = doc.company
    accounts = doc.accounts or []
    wallet_account = _get_wallet_account(company)
    credit_wallet = any(a.account == wallet_account and float(a.credit_in_account_currency or 0) > 0 for a in accounts)
    for a in accounts:
        if a.party_type == 'Customer' and float(a.debit_in_account_currency or 0) > 0 and credit_wallet:
            amount = float(a.debit_in_account_currency)
            wt = frappe.get_doc({
                'doctype': 'Wallet Transaction',
                'posting_date': frappe.utils.nowdate(),
                'party_type': 'Customer',
                'party': a.party,
                'transaction_type': 'Transfer Out',  # reverse effect
                'amount': amount,
                'reference_doctype': 'Journal Entry',
                'reference_name': doc.name,
                'remarks': 'Reverse Top-Up due to JE cancel'
            })
            wt.insert(ignore_permissions=True)

def _get_wallet_account(company):
    # naive lookup by name; you can change to a Company field/setting
    abbr = frappe.get_value("Company", company, "abbr")
    name = f"Wallet Balance - {abbr}"
    acc = frappe.get_value("Account", {"name": name})
    if not acc:
        frappe.throw(f"Wallet account {name} not found. Create it under Receivables.")
    return name
