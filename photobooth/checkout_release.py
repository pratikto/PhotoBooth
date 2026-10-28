"""Two-phase Sandbox occupancy release; financial/media rights are never reset."""
from photobooth.checkout_store import CheckoutConflict, identifier


def latest(store, order_id, booth_id):
    with store.lock:
        store._row(order_id,booth_id)
        row=store.db.execute('SELECT * FROM checkout_releases WHERE order_id=? ORDER BY generation DESC LIMIT 1',
                             (order_id,)).fetchone()
        return dict(row) if row else None


def prepare(store, order_id, booth_id, operation_id, actor):
    identifier(operation_id,minimum=16);identifier(actor,maximum=96)
    with store.write():
        order=store._row(order_id,booth_id)
        old=store.db.execute('SELECT * FROM checkout_releases WHERE operation_id=?',(operation_id,)).fetchone()
        if old:
            if old['order_id']!=order_id or old['booth_id']!=booth_id:
                raise CheckoutConflict('Release operation mismatch')
            return dict(old)
        capability=store.db.execute('SELECT * FROM checkout_customer_capabilities WHERE order_id=?',(order_id,)).fetchone()
        rights=store.fulfillment(order_id,booth_id)
        if (order['closed'] or order['state']!='PAID' or rights['obligation_state']!='OWED'
                or not capability or capability['revoked'] or capability['expires_at']<=store.now()):
            raise CheckoutConflict('Original recoverable paid rights required')
        previous=latest(store,order_id,booth_id)
        if previous and previous['state']=='PREPARED':
            raise CheckoutConflict('Original release operation required')
        fence=store.service_fence(order_id,booth_id)
        fence=store._rotate_service_fence(order_id,booth_id,fence['generation'] if fence else 0,suspended=True)
        store.db.execute('INSERT INTO checkout_releases VALUES (?,?,?,?,?,?,?,NULL,?,NULL)',
            (operation_id,order_id,booth_id,fence['generation'],'PREPARED','OPERATOR_SUSPEND',actor,store.now()))
        return latest(store,order_id,booth_id)


def acknowledge(store, order_id, booth_id, operation_id, isolation_id):
    identifier(operation_id,minimum=16);identifier(isolation_id,minimum=16)
    with store.write():
        store._row(order_id,booth_id)
        row=store.db.execute('SELECT * FROM checkout_releases WHERE operation_id=?',(operation_id,)).fetchone()
        if not row or row['order_id']!=order_id or row['booth_id']!=booth_id:
            raise CheckoutConflict('Prepared original release required')
        if row['state'] in {'ACKED','REACQUIRED'}:
            if row['isolation_id']!=isolation_id:
                raise CheckoutConflict('Isolation receipt mismatch')
            return dict(row)
        fence=store.service_fence(order_id,booth_id)
        if not fence or not fence['suspended'] or fence['generation']!=row['generation']:
            raise CheckoutConflict('Original suspended generation required')
        store.db.execute("UPDATE checkout_releases SET state='ACKED',isolation_id=?,acked_at=? WHERE operation_id=?",
                         (isolation_id,store.now(),operation_id))
        store.db.execute('UPDATE checkouts SET closed=1 WHERE id=?',(order_id,))
        store.db.execute("UPDATE checkout_fulfillments SET state='SUSPENDED',updated_at=? WHERE order_id=?",
                         (store.now(),order_id))
        return latest(store,order_id,booth_id)


def reacquire(store, order):
    """Caller has verified customer proof/current settlement and owns write()."""
    release=latest(store,order['id'],order['booth_id'])
    if not release or release['state']!='ACKED' or not order['closed'] or order['state']!='PAID':
        raise CheckoutConflict('Original suspended visit required')
    require_free_booth(store,order)
    fence=store.service_fence(order['id'],order['booth_id'])
    if not fence or not fence['suspended'] or fence['generation']!=release['generation']:
        raise CheckoutConflict('Original release generation required')
    store._rotate_service_fence(order['id'],order['booth_id'],fence['generation'],suspended=False)
    store.db.execute('UPDATE checkouts SET closed=0 WHERE id=?',(order['id'],))
    store.db.execute("UPDATE checkout_releases SET state='REACQUIRED' WHERE operation_id=?",(release['operation_id'],))
    state={'NONE':'OWED','RESERVED':'ALLOCATED' if store.fulfillment(order['id'],order['booth_id'])['transaction_id'] else 'OWED',
           'STARTED':'STARTED','COMPLETED':'COMPOSED'}[order['service_state']]
    store.db.execute('UPDATE checkout_fulfillments SET state=?,updated_at=? WHERE order_id=?',
                     (state,store.now(),order['id']))
    return store._row(order['id'],order['booth_id'])


def require_free_booth(store,order):
    other=store.db.execute('''SELECT 1 FROM checkouts WHERE booth_id=? AND id!=?
        AND closed=0 AND state NOT IN ('EXPIRED','CANCELLED','FAILED') AND service_state!='COMPLETED' ''',
        (order['booth_id'],order['id'])).fetchone()
    if other:
        raise CheckoutConflict('Booth is serving another customer')
