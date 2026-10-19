"""Dependency-injected FastAPI sandbox application for FEAT-020.

This is a staging-only API factory, not a production deployment.
"""
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict


class NewOrder(BaseModel):
    model_config = ConfigDict(extra="forbid")
    quantities: dict[str, int]


def create_app(service, authenticator):
    app = FastAPI(title="MEONG QRIS Sandbox")

    def booth_identity(booth_id, authorization):
        identity = authenticator.authenticate(booth_id, authorization)
        if identity is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        return identity

    @app.get("/api/health")
    def health():
        return {"status": "ok", "mode": "sandbox"}

    @app.post("/api/orders", status_code=201)
    def create_order(body: NewOrder, x_booth_id: str = Header(default=""),
                     authorization: str = Header(default="")):
        booth_id = booth_identity(x_booth_id, authorization)
        try:
            return service.create_order(booth_id, body.quantities)
        except ValueError as error:
            raise HTTPException(status_code=422, detail="Invalid checkout") from error

    @app.get("/api/orders/{order_id}")
    def order_status(order_id: str, x_booth_id: str = Header(default=""),
                     authorization: str = Header(default="")):
        booth_id = booth_identity(x_booth_id, authorization)
        result = service.status(order_id, booth_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Order not found")
        return result

    @app.post("/api/orders/{order_id}/claim")
    def claim_order(order_id: str, x_booth_id: str = Header(default=""),
                    authorization: str = Header(default="")):
        booth_id = booth_identity(x_booth_id, authorization)
        if service.status(order_id, booth_id) is None:
            raise HTTPException(status_code=404, detail="Order not found")
        if not service.claim(order_id, booth_id):
            raise HTTPException(status_code=409, detail="Order not claimable")
        return {"claimed": True}

    return app
