import json

import boto3
from botocore.config import Config as BotoConfig

from app.core.config import settings
from app.schemas.ai import SuggestionRequest
from app.services.ai.prompts import SYSTEM_PROMPT
from app.services.ai.provider import LLMProvider


class BedrockProvider(LLMProvider):
    """AWS Bedrock LLM provider implementation."""

    def __init__(self):
        self.client = boto3.client(
            "bedrock-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            config=BotoConfig(read_timeout=5, connect_timeout=2),
        )
        self.model_id = settings.AWS_BEDROCK_MODEL_ID

    async def classify_field(self, request: SuggestionRequest) -> dict:
        user_message = json.dumps(
            {
                "label": request.label,
                "language": request.language.value,
                "country": request.country.value,
                "context": request.context,
            },
            ensure_ascii=False,
        )

        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 512,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": user_message}],
            }
        )

        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body,
            contentType="application/json",
            accept="application/json",
        )

        response_body = json.loads(response["body"].read())
        content = response_body["content"][0]["text"]
        return json.loads(content)
