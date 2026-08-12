# STEP 6: PRODUCTION-READY PAYMENT, SUBSCRIPTION, BILLING, CREDIT, COUPON & USAGE-LIMIT SYSTEM

## Architectural Highlights

### 1. Unified Payment Gateway Abstraction
- Abstract `PaymentGateway` base class (`app.services.billing.gateways.base`).
- Provider implementations:
  - `StripeGateway`: Full Stripe API checkout session, billing portal, and subscription lifecycle handling.
  - `RazorpayGateway`: Razorpay order creation, payment signature verification, and subscription integration.
  - `MockGateway`: Test suite and offline development provider.
- `get_payment_gateway(provider)` factory decouples the rest of the application from provider-specific logic.

### 2. Comprehensive Database Schema
- **Plans & Features**: `plans` and `plan_features` with multi-currency monthly/yearly pricing, trial periods, and feature flag rules.
- **Subscriptions**: `subscriptions` storing user plan, status lifecycle (`FREE`, `TRIALING`, `ACTIVE`, `PAST_DUE`, `CANCELED`, `EXPIRED`, `PENDING`), provider references, current period dates, and cancellation state.
- **Payments & Invoices**: `payments`, `invoices`, `invoice_items`, and `refunds` using `NUMERIC(12, 2)` precision.
- **Coupons & Redemptions**: `coupons` and `coupon_redemptions` supporting percentage or fixed discounts, usage caps, and expiration limits.
- **Usage & Quotas**: `usage_limits` and `usage_records` tracking channel syncs, video audits, keyword searches, and AI scripts.
- **Idempotency**: `webhook_events` tracking received webhook event hashes and idempotency status.

### 3. Centralized Entitlement & Limits Engine
- `EntitlementService`: Unified service providing `can_use_feature`, `check_limit`, and entitlement summaries across all platform endpoints.
- FastAPI Dependencies:
  - `require_active_subscription`: Enforces active subscription status.
  - `require_feature(feature_code)`: Restricts routes based on plan features.
  - `require_usage_limit(metric_key)`: Blocks requests when user hits quota limits.
  - `require_remaining_credits(min_credits)`: Connects with Step 5 AI CreditSystem.

### 4. Verified Webhooks & Security
- `WebhookProcessor`: Handles signature validation, event deduplication, and server-side state transitions.
- Strictly activates or upgrades subscriptions **only** upon verified provider webhook confirmation or signature check.

### 5. Automated Background Tasks (Celery)
- Trial expiration warnings & transitions.
- Subscription renewal processing & credit replenishment.
- Past-due dunning alerts.

### 6. API Endpoints
- User Billing: `/api/v1/billing/*` (`/plans`, `/subscription`, `/checkout`, `/portal`, `/cancel`, `/resume`, `/change-plan`, `/payments`, `/invoices`, `/usage`, `/coupons/validate`, `/topup`)
- Webhooks: `/api/v1/webhooks/*` (`/stripe`, `/razorpay`)
- Admin Billing: `/api/v1/admin/billing/*` (`/plans`, `/subscriptions`, `/payments`, `/invoices`, `/refunds`, `/coupons`, `/revenue`, `/webhooks`)
