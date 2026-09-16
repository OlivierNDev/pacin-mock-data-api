# PACIN Mock API — Key Transformer Credentials

Use these values when registering each rail as a **source** in the PACIN Key Transformer.

> **Base URL for all sources:** `https://pacin-mock-data-api.onrender.com`  
> (or your Render/ngrok URL if self-hosted)

---

## How to register (3-step flow)

1. **Key Transformer → Add source** — paste the credentials below for the rail you want
2. **Key Transformer → Gen Token** — generates a 16-char token, valid ~5 seconds
3. **Rails → open the rail → paste token** into *Transformer Token* field within 5s

Credentials show **once** on save; you cannot re-view them — only replace.

---

## MTN MoMo Rail

| Field | Value |
|---|---|
| **Environment** | Sandbox |
| **API user / Client ID** | `a1b2c3d4-momo-4f5e-8a7b-1c2d3e4f5a6b` |
| **API key** | `pacin_momo_test_sk_a7f3c9d2e8b14f6a` |
| **Subscription key** | `momo_subkey_7f3c9d2e8b14f6a93d` |
| **Webhook secret** | `momo_webhook_secret_x9k2p` |
| **Base URL** | `https://pacin-mock-data-api.onrender.com` |
| **Enabled** | ✅ On |

---

## Airtel Money Rail

| Field | Value |
|---|---|
| **Environment** | Sandbox |
| **API user / Client ID** | `e5f6a7b8-tel-4d9c-ce1f-5a6b7c8d9e0f` |
| **API key** | `pacin_tel_test_sk_e1f4a8b2c6d9e3f7` |
| **Subscription key** | `tel_subkey_f4a8b2c6d9e3f7e1` |
| **Webhook secret** | `tel_webhook_secret_m7r4q` |
| **Base URL** | `https://pacin-mock-data-api.onrender.com` |
| **Enabled** | ✅ On |

---

## Orange Money Rail

| Field | Value |
|---|---|
| **Environment** | Sandbox |
| **API user / Client ID** | `e5f6a7b8-tel-4d9c-ce1f-5a6b7c8d9e0f` |
| **API key** | `pacin_tel_test_sk_e1f4a8b2c6d9e3f7` |
| **Subscription key** | `tel_subkey_f4a8b2c6d9e3f7e1` |
| **Webhook secret** | `tel_webhook_secret_m7r4q` |
| **Base URL** | `https://pacin-mock-data-api.onrender.com` |
| **Enabled** | ✅ On |

---

## M-Pesa Daraja Rail (Bank / Open Banking)

| Field | Value |
|---|---|
| **Environment** | Sandbox |
| **API user / Client ID** | `b2c3d4e5-bank-4a6f-9b8c-2d3e4f5a6b7c` |
| **API key** | `pacin_bank_test_sk_b2e5f8a1d4c7e9f3` |
| **Subscription key** | `bank_subkey_e5f8a1d4c7e9f3b2d` |
| **Webhook secret** | `bank_webhook_secret_n8s5t` |
| **Base URL** | `https://pacin-mock-data-api.onrender.com` |
| **Enabled** | ✅ On |

---

## Mono Rail (Open Banking)

| Field | Value |
|---|---|
| **Environment** | Sandbox |
| **API user / Client ID** | `b2c3d4e5-bank-4a6f-9b8c-2d3e4f5a6b7c` |
| **API key** | `pacin_bank_test_sk_b2e5f8a1d4c7e9f3` |
| **Subscription key** | `bank_subkey_e5f8a1d4c7e9f3b2d` |
| **Webhook secret** | `bank_webhook_secret_n8s5t` |
| **Base URL** | `https://pacin-mock-data-api.onrender.com` |
| **Enabled** | ✅ On |

---

## Pngme Rail (Identity / Credit)

| Field | Value |
|---|---|
| **Environment** | Sandbox |
| **API user / Client ID** | `d4e5f6a7-insur-4c8b-bd0e-4f5a6b7c8d9e` |
| **API key** | `pacin_insur_test_sk_d9e3f6a4b7c2e8f1` |
| **Subscription key** | `insur_subkey_e3f6a4b7c2e8f1d9` |
| **Webhook secret** | `insur_webhook_secret_p3v7w` |
| **Base URL** | `https://pacin-mock-data-api.onrender.com` |
| **Enabled** | ✅ On |

---

## Authentication

The mock API accepts **any of these three** auth methods — whichever the Key Transformer sends:

```
X-API-Key: <api_key>
Ocp-Apim-Subscription-Key: <subscription_key>   # MTN MoMo / Azure style
Authorization: Bearer <client_id>               # OAuth / Mono / Pngme style
```

---

## Test endpoints per rail

| Rail | Endpoint | Auth key to use |
|---|---|---|
| MTN MoMo / Airtel / Orange | `GET /momo/{subject_id}` | momo or telecom API key |
| M-Pesa / Mono | `GET /bank/{subject_id}` | bank API key |
| Pngme | `GET /insurance/{subject_id}` | insurance API key |
| Utility | `GET /utility/{subject_id}` | utility API key |
| Telecom | `GET /telecom/{subject_id}` | telecom API key |

**Test subjects:** `PACIN_TEST_001` (good profile) · `PACIN_TEST_002` (risky)

---

## Do I need to host it?

**Yes.** The Key Transformer at `app.pacinnetwork.com` is cloud-hosted and needs a public URL.
GitHub only stores the code — it cannot serve API requests.

**Recommended: Render free tier (3 steps)**
1. Go to [render.com](https://render.com) and sign in with GitHub
2. New → Web Service → connect `OlivierNDev/pacin-mock-data-api`
3. Click **Deploy** — the `render.yaml` already configures everything

Your URL will be: `https://pacin-mock-data-api.onrender.com`  
Update the **Base URL** field in each Key Transformer source to that URL.

> ⚠️ Render free tier **spins down after 15 min of inactivity** (cold start ~30s).  
> This is fine for testing. For continuous use, upgrade to Render Starter ($7/mo).
