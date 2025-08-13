
import frappe

def sum_balance(party_type, party):
    val = frappe.db.sql('''
        SELECT COALESCE(SUM(
            CASE
              WHEN transaction_type IN ('Top-Up','Transfer In','Reservation Release') THEN amount
              WHEN transaction_type IN ('Consumption','Transfer Out','Reservation') THEN -amount
              ELSE 0
            END
        ), 0)
        FROM `tabWallet Transaction`
        WHERE party_type=%s AND party=%s
    ''', (party_type, party))
    return float(val[0][0] or 0)

def get_running_balance(party_type, party):
    res = frappe.db.sql('''
        SELECT running_balance FROM `tabWallet Transaction`
        WHERE party_type=%s AND party=%s
        ORDER BY posting_date DESC, creation DESC
        LIMIT 1
    ''', (party_type, party))
    return float(res[0][0]) if res else None
