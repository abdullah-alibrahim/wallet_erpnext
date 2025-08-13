
frappe.ui.form.on('Sales Invoice', {
  refresh: function(frm) {
    if (!frm.doc.wallet_receivable_account && frm.doc.company) {
      frappe.db.get_value('Company', frm.doc.company, 'abbr').then(r => {
        if (r && r.message && r.message.abbr) {
          frm.set_value('wallet_receivable_account', 'Wallet Balance - ' + r.message.abbr);
        }
      });
    }
  },
  wallet_sale: function(frm) {
    if (frm.doc.wallet_sale) {
      if (!frm.doc.wallet_receivable_account) {
        frappe.throw('Wallet Receivable Account is required.');
      }
      frm.set_value('debit_to', frm.doc.wallet_receivable_account);
      frm.set_df_property('debit_to', 'read_only', 1);
    } else {
      frm.set_df_property('debit_to', 'read_only', 0);
      // trigger customer to reload default receivable
      if (frm.doc.customer) frm.trigger('customer');
    }
  }
});
