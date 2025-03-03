from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

import httpx

class ModerationPerspectiveApiTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        text: str = tool_parameters.get("text")
        threshold = tool_parameters.get("threshold") or 0.5

        attributes = [
            "TOXICITY",
            "SEVERE_TOXICITY",
            "IDENTITY_ATTACK",
            "INSULT",
            "PROFANITY",
            "THREAT",
        ]

        url = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
        headers = {
            "x-goog-api-key": self.runtime.credentials['api_key'],
            "Content-Type": "application/json",
        }
        response = httpx.post(url, headers=headers, json={
            "comment": { "text": text },
            "requestedAttributes": { attribute: {} for attribute in attributes },
        })

        if response.is_success:
            json_response = response.json()
            scores = json_response["attributeScores"]

            unsafe_score = 0
            flagged_categories = []
            category_scores = {}
            for name, scores in scores.items():
                score = scores["summaryScore"]["value"]
                category_scores[name.lower()] = score
                unsafe_score = max(score, unsafe_score)
                if score >= threshold:
                    flagged_categories.append(name.lower())

            flagged = len(flagged_categories) > 0
            return [
                self.create_json_message(json_response),
                self.create_text_message("true" if flagged else "false"),
                self.create_variable_message("flagged", flagged),
                self.create_variable_message("unsafe_score", unsafe_score),
                self.create_variable_message("flagged_categories", flagged_categories),
                self.create_variable_message("category_scores", category_scores),
            ]
        else:
            raise ValueError(response.text)

