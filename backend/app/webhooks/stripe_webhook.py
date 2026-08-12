from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.post("/stripe")
async def handle_stripe_webhook(request: Request):
    payload = await request.body()
    # Handle Stripe Webhook events (invoice.payment_succeeded, customer.subscription.created)
    return {"received": True}
