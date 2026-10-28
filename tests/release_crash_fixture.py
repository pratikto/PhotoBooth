"""Abrupt SQLite WAL release crash boundary; existing synthetic order only."""
import os,sys
from photobooth.checkout_store import CheckoutStore
from photobooth import checkout_release
store=CheckoutStore(sys.argv[1]);oid=sys.argv[2];phase=sys.argv[3]
checkout_release.prepare(store,oid,'PB001','e'*32,'crash-fixture')
if phase=='acked':checkout_release.acknowledge(store,oid,'PB001','e'*32,'f'*32)
os._exit(71)
