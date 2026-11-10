"""Trusted backend original freeze. No provider/Drive allocation or CCP grant."""
from photobooth.post_preview_checkout import PrivateDraftCheckout,ChargeReadiness
from photobooth.post_preview_readiness import TrustedFreezeReadiness
from photobooth.post_preview_readiness_bridge import BackendChargeReadiness
from photobooth.post_preview_store import DraftHeld


class OriginalSandboxFreeze:
    def __init__(self,checkout,templates,readiness,booth_id):
        if (type(checkout) is not PrivateDraftCheckout or type(readiness) is not BackendChargeReadiness
                or readiness.checkout is not checkout or tuple(templates)!=readiness.templates):
            raise ValueError('Exact original backend freeze dependencies required')
        self.checkout,self.templates,self.readiness=checkout,tuple(templates),readiness
        self.booth_id=booth_id

    def scope(self,lease,*,revision,expected_amount):
        if lease.booth_id!=self.booth_id:raise DraftHeld('Original booth required')
        return self.checkout.freeze_scope(lease,self.templates,revision=revision,expected_amount=expected_amount)

    def freeze(self,lease,*,revision,expected_amount,expected_scope):
        scope=self.scope(lease,revision=revision,expected_amount=expected_amount)
        if scope!=expected_scope:raise DraftHeld('Original freeze request changed')
        report=self.readiness.for_freeze(scope)
        if type(report) is not TrustedFreezeReadiness:
            raise DraftHeld('Exact independently observed pre-freeze readiness required')
        def fresh():report.require(scope,now=self.checkout.ledger.now())
        fresh()
        # Lower-bound capacity1 is derived only from complete fresh backend
        # evidence, never from client fields. Original primitive remains shared
        # with explicit mock fixtures; this protected caller has stricter gates.
        return self.checkout.freeze(lease,self.templates,revision=revision,
            expected_amount=expected_amount,expected_contract_sha256=scope.contract_sha256,
            readiness=ChargeReadiness(True,True,True,True,True,True,True,1),before_commit=fresh)
