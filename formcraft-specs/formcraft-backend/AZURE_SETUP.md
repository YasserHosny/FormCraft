# Azure Document Intelligence Setup

## Quick Start

Add these lines to `/media/yasser/Work/Projects/formcraft-backend/.env`:

```bash
# Azure Document Intelligence (OCR)
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://YOUR_RESOURCE.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_api_key_here
```

## Creating Azure Resource

### Option 1: Azure Portal (Recommended)

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Document Intelligence" (formerly "Form Recognizer")
4. Click "Create"
5. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Region**: Choose closest to your servers (e.g., East US, West Europe)
   - **Name**: formcraft-ocr (or your choice)
   - **Pricing Tier**: Free F0 (500 pages/month) or Standard S0
6. Click "Review + Create" → "Create"
7. Wait for deployment (~2 minutes)
8. Go to resource → "Keys and Endpoint" tab
9. Copy **KEY 1** and **Endpoint URL**

### Option 2: Azure CLI

```bash
# Login
az login

# Create resource group
az group create --name formcraft-rg --location eastus

# Create Document Intelligence resource
az cognitiveservices account create \
  --name formcraft-ocr \
  --resource-group formcraft-rg \
  --kind FormRecognizer \
  --sku F0 \
  --location eastus \
  --yes

# Get endpoint and key
az cognitiveservices account show \
  --name formcraft-ocr \
  --resource-group formcraft-rg \
  --query "properties.endpoint" -o tsv

az cognitiveservices account keys list \
  --name formcraft-ocr \
  --resource-group formcraft-rg \
  --query "key1" -o tsv
```

## Pricing Tiers

| Tier | Pages/Month | Cost | Use Case |
|------|-------------|------|----------|
| **F0 (Free)** | 500 | Free | Development, POC |
| **S0 (Standard)** | Unlimited | $1.50/1000 pages | Production |

**Free tier limitations:**
- 500 pages/month
- 20 requests/minute
- Shared infrastructure

**Recommended for production:**
- Start with Free tier
- Upgrade to S0 when exceeding 500 pages/month
- Enable rate limiting in backend to avoid overages

## Testing OCR

```bash
# Test with cURL
curl -X POST "https://YOUR_RESOURCE.cognitiveservices.azure.com/formrecognizer/documentModels/prebuilt-layout:analyze?api-version=2023-07-31" \
  -H "Content-Type: application/json" \
  -H "Ocp-Apim-Subscription-Key: YOUR_KEY" \
  -d '{"urlSource": "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-layout.pdf"}'
```

Expected response: `202 Accepted` with `Operation-Location` header.

## Troubleshooting

**"401 Unauthorized"**
- Check API key is correct
- Verify endpoint URL matches your resource

**"403 Forbidden"**
- Check resource is active (not suspended)
- Verify subscription has not exceeded quota

**"429 Too Many Requests"**
- Free tier: 20 requests/minute limit
- Add rate limiting or upgrade to Standard

**"Endpoint not found"**
- Ensure endpoint URL ends with `/`
- Verify region matches resource region

## Security Best Practices

1. **Never commit credentials** to Git
   - Add `.env` to `.gitignore`
   - Use `.env.example` template without actual keys

2. **Use separate keys** for dev/staging/production
   - Create separate Azure resources per environment
   - Rotate keys quarterly

3. **Enable Azure monitoring**
   - Set up alerts for quota limits
   - Monitor for unusual API usage

4. **Regenerate keys** if exposed
   - Azure Portal → Resource → Keys → Regenerate
   - Update `.env` file
   - Restart backend

## Monitoring & Costs

Check usage in Azure Portal:
- Resource → Metrics → Total Calls
- Resource → Cost Analysis → Estimated costs

Set up budget alerts:
- Cost Management → Budgets → Create
- Alert threshold: 80% of monthly limit

## Alternative: Tesseract (Fallback)

If Azure is not available, fallback to Tesseract:

```bash
# Install Tesseract
apt-get install tesseract-ocr tesseract-ocr-ara

# Install Python wrapper
pip install pytesseract==0.3.10

# Add to .env
USE_TESSERACT_FALLBACK=true
```

**Note**: Tesseract accuracy for Arabic is ~80-85% vs Azure's 95%+.
