from uuid import uuid4

from app.schemas.billing import (
    BillingOptionsResponse,
    BillingPurchaseListResponse,
    BillingPurchaseResponse,
    PayGatewayWebhookRequest,
    PayGatewayWebhookResponse,
    PurchaseCreateRequest,
    PurchaseCreateResponse,
    PurchaseVerifyResponse,
    RefundCreateRequest,
    RefundResponse,
)


def test_billing_options_contract_shape():
    payload = {
        "currency": "EGP",
        "current_tier": "starter",
        "tiers": [
            {
                "tier": "professional",
                "amount_minor": 250000,
                "currency": "EGP",
                "available": True,
            }
        ],
        "addons": [
            {
                "purpose": "seats",
                "unit_amount_minor": 10000,
                "currency": "EGP",
                "min_quantity": 1,
                "max_quantity": 500,
                "available": True,
            }
        ],
    }

    assert BillingOptionsResponse(**payload).tiers[0].tier == "professional"


def test_purchase_create_contract_shapes():
    request = PurchaseCreateRequest(
        purpose="subscription_tier",
        target={"tier": "professional"},
        return_url="https://app.example/billing",
    )
    response = PurchaseCreateResponse(
        purchase_id=uuid4(),
        status="created",
        amount_minor=250000,
        currency="EGP",
        checkout={
            "provider": "paygateway",
            "client_token": "token",
            "requires_action": False,
        },
    )

    assert request.target["tier"] == "professional"
    assert response.checkout is not None


def test_purchase_verify_and_history_contract_shapes():
    purchase_id = uuid4()
    org_id = uuid4()
    purchase = BillingPurchaseResponse(
        id=purchase_id,
        organization_id=org_id,
        purpose="subscription_tier",
        target={"tier": "professional"},
        amount_minor=250000,
        currency="EGP",
        status="succeeded",
        created_at="2026-06-19T10:00:00Z",
    )
    verify = PurchaseVerifyResponse(
        purchase_id=purchase_id,
        status="succeeded",
        fulfilled=True,
        message_key="billing.purchase.fulfilled",
    )
    history = BillingPurchaseListResponse(items=[purchase])

    assert verify.fulfilled is True
    assert history.items[0].id == purchase_id


def test_webhook_and_refund_contract_shapes():
    purchase_id = uuid4()
    webhook = PayGatewayWebhookRequest(
        event_id="evt_1",
        event_type="payment.succeeded",
        payment_id="pay_1",
        purchase_reference=purchase_id,
    )
    webhook_response = PayGatewayWebhookResponse(
        received=True,
        purchase_id=purchase_id,
        status="succeeded",
    )
    refund_request = RefundCreateRequest(reason="Customer request")
    refund_response = RefundResponse(
        refund_id=uuid4(),
        purchase_id=purchase_id,
        status="succeeded",
        reversal_status="applied",
        amount_minor=250000,
        currency="EGP",
        message_key="billing.refund.applied",
    )

    assert webhook.purchase_reference == purchase_id
    assert webhook_response.received is True
    assert refund_request.reason == "Customer request"
    assert refund_response.reversal_status == "applied"
