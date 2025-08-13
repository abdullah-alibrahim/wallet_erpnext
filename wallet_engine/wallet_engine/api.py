
import frappe
from frappe import _
from wallet_engine.wallet_engine.balance import get_running_balance, sum_balance

@frappe.whitelist()
def wallet_balance(party_type, party):
    bal = get_running_balance(party_type, party)
    if bal is None:
        bal = sum_balance(party_type, party)
    return {'party_type': party_type, 'party': party, 'balance': bal}

@frappe.whitelist()
def wallet_transactions(party_type, party, limit=50, from_date=None, to_date=None):
    filters = {'party_type': party_type, 'party': party}
    conditions = "WHERE party_type=%s AND party=%s"
    params = [party_type, party]
    if from_date:
        conditions += " AND posting_date >= %s"
        params.append(from_date)
    if to_date:
        conditions += " AND posting_date <= %s"
        params.append(to_date)
    limit = int(limit or 50)
    rows = frappe.db.sql(f'''
        SELECT posting_date, transaction_type, amount, running_balance,
               reference_doctype, reference_name, remarks
        FROM `tabWallet Transaction`
        {conditions}
        ORDER BY posting_date DESC, creation DESC
        LIMIT {limit}
    ''', tuple(params), as_dict=True)
    return rows

@frappe.whitelist()
def wallet_transfer(from_party_type, from_party, to_party_type, to_party, amount, remarks=None):
    amount = float(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be positive."))
    wt = frappe.get_doc({
        'doctype': 'Wallet Transfer',
        'from_party_type': from_party_type,
        'from_party': from_party,
        'to_party_type': to_party_type,
        'to_party': to_party,
        'amount': amount,
        'remarks': remarks or ''
    }).insert()
    wt.submit()
    return {'status': 'ok', 'name': wt.name}

@frappe.whitelist()
def wallet_topup_via_journal_entry(company, party, amount, remarks=None):
    amount = float(amount)
    if amount <= 0:
        frappe.throw(_("Amount must be positive."))

    abbr = frappe.get_value("Company", company, "abbr")
    wallet_account = f"Wallet Balance - {abbr}"
    debtors = frappe.get_value('Company', company, 'default_receivable_account')

    if not frappe.db.exists("Account", wallet_account):
        frappe.throw(_("Wallet account {0} not found").format(wallet_account))

    je = frappe.get_doc({
        'doctype': 'Journal Entry',
        'voucher_type': 'Debit Note',
        'company': company,
        'user_remark': remarks or 'Wallet Top-Up',
        'accounts': [
            {'account': debtors, 'party_type': 'Customer', 'party': party, 'debit_in_account_currency': amount},
            {'account': wallet_account, 'credit_in_account_currency': amount},
        ]
    }).insert()
    je.submit()
    return {'status': 'ok', 'journal_entry': je.name}
