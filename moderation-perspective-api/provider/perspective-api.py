from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

import httpx

class ModerationPerspectiveApiProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
            headers = {
                "x-goog-api-key": credentials['api_key'],
                "Content-Type": "application/json",
            }
            response = httpx.post(url, headers=headers, json={
                "comment": { "text": "validate credentials" },
                "languages": ["en"],
                "requestedAttributes": { "TOXICITY": {} },
            })

            if response.is_success:
                pass
            else:
                raise ToolProviderCredentialValidationError(response.text)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
