# PACIN Mock Data Provider API

A FastAPI service that simulates **5 Rwandan financial data providers** for testing the PACIN Key Transformer and Credit Intelligence pipeline.

## Test Subjects

| Name | subject_id | 16-digit NID | Profile | Location |
|------|-----------|--------------|---------|----------|
| Alice Uwimana | `PACIN_TEST_001` | **`1199850101110001`** | good_credit | Kigali, Gasabo |
| Jean-Pierre Habimana | `PACIN_TEST_002` | **`1199760202220002`** | risky_thin_file | Musanze |

24 months of data (2024-09 to 2026-08) per subject across all 5 sources.

### NID Lookup
```bash
# Lookup by NID (direct)
curl https://pacin-mock-data-api.onrender.com/subjects/by-nid/1199850101110001

# Filter subjects list by NID
curl "https://pacin-mock-data-api.onrender.com/subjects?nid=1199760202220002"
```

## API Keys (Test)

| Source | API Key | Header |
|--------|---------|--------|
| MoMo | `pacin_momo_test_sk_a7f3c9d2e8b14f6a` | `X-API-Key` |
| Bank | `pacin_bank_test_sk_b2e5f8a1d4c7e9f3` | `X-API-Key` |
| Utility | `pacin_util_test_sk_c4d7e2f9a1b8c3d6` | `X-API-Key` |
| Insurance | `pacin_insur_test_sk_d9e3f6a4b7c2e8f1` | `X-API-Key` |
| Telecom | `pacin_tel_test_sk_e1f4a8b2c6d9e3f7` | `X-API-Key` |

## Base URL

After deploying to Render: `https://pacin-mock-data-api.onrender.com`

## Endpoints

```
GET  /health                          # No auth
GET  /subjects                        # No auth — includes national_id field
GET  /subjects?nid={16-digit-nid}     # No auth — filter by NID
GET  /subjects/by-nid/{nid}           # No auth — lookup by 16-digit NID
GET  /momo/{subject_id}               # X-API-Key: momo key
GET  /momo/{subject_id}/summary
GET  /bank/{subject_id}               # X-API-Key: bank key
GET  /bank/{subject_id}/loans
GET  /utility/{subject_id}            # X-API-Key: utility key
GET  /insurance/{subject_id}          # X-API-Key: insurance key
GET  /telecom/{subject_id}            # X-API-Key: telecom key
POST /webhook/register                # Any valid key
POST /webhook/test/{source_type}
GET  /webhook/events/{source_type}
```

## Quick Test

```bash
# Health check
curl https://pacin-mock-data-api.onrender.com/health

# List subjects
curl https://pacin-mock-data-api.onrender.com/subjects

# Fetch MoMo data for Alice
curl -H "X-API-Key: pacin_momo_test_sk_a7f3c9d2e8b14f6a" \
  https://pacin-mock-data-api.onrender.com/momo/PACIN_TEST_001/summary

# Fetch bank loans for Jean-Pierre
curl -H "X-API-Key: pacin_bank_test_sk_b2e5f8a1d4c7e9f3" \
  https://pacin-mock-data-api.onrender.com/bank/PACIN_TEST_002/loans

# Register a webhook
curl -X POST https://pacin-mock-data-api.onrender.com/webhook/register \
  -H "X-API-Key: pacin_momo_test_sk_a7f3c9d2e8b14f6a" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-pacin-backend.com/webhooks", "source_type": "momo", "secret": "your_secret"}'
```

## PACIN Key Transformer Integration

Register all 5 keys in Super Admin -> Data Sources:

1. MoMo: endpoint `https://pacin-mock-data-api.onrender.com/momo/{subject_id}`, key `pacin_momo_test_sk_a7f3c9d2e8b14f6a`
2. Bank: endpoint `.../bank/{subject_id}`, key `pacin_bank_test_sk_b2e5f8a1d4c7e9f3`
3. Utility: endpoint `.../utility/{subject_id}`, key `pacin_util_test_sk_c4d7e2f9a1b8c3d6`
4. Insurance: endpoint `.../insurance/{subject_id}`, key `pacin_insur_test_sk_d9e3f6a4b7c2e8f1`
5. Telecom: endpoint `.../telecom/{subject_id}`, key `pacin_tel_test_sk_e1f4a8b2c6d9e3f7`

Once registered, the Transformer generates one PACIN Token -> fetches all 5 in parallel -> returns unified payload.

## Deploy to Render (3 steps)

1. Fork this repo to your GitHub account
2. Go to render.com -> New Web Service -> Connect your GitHub repo
3. Render auto-detects `render.yaml` -> click Deploy

Free tier URL: `https://pacin-mock-data-api.onrender.com`

Note: Render free tier spins down after 15min inactivity. For testing, just hit `/health` to wake it up.

## Interactive Docs

Visit `/docs` for full Swagger UI after deploying.
