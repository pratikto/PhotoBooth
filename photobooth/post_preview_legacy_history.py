"""Original legacy readiness policy shared by charge and read-only startup.

Requires the caller's original SQLite ownership/snapshot. Never changes finance,
closes visits or grants media; true is only one local readiness observation.
"""


def legacy_history_clear(db,booth_id):
    rows=db.execute('SELECT * FROM checkouts WHERE booth_id=?',(booth_id,)).fetchall()
    for order in rows:
        if not order['closed'] or order['state'] not in {'PAID','EXPIRED','CANCELLED','FAILED'}:
            return False
        if order['state']=='PAID':
            rights=db.execute('SELECT * FROM checkout_fulfillments WHERE order_id=? AND booth_id=?',
                             (order['id'],booth_id)).fetchone()
            if rights is None:return False
            if rights['obligation_state']=='FULFILLED':continue
            release=db.execute('SELECT * FROM checkout_releases WHERE order_id=? '
                               'ORDER BY generation DESC LIMIT 1',(order['id'],)).fetchone()
            fence=db.execute('SELECT * FROM checkout_service_fences WHERE order_id=?',
                             (order['id'],)).fetchone()
            if (not release or release['state']!='ACKED' or not release['isolation_id']
                    or not fence or not fence['suspended'] or fence['generation']!=release['generation']):
                return False
    return True
