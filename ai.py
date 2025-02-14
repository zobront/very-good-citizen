# ai.py
from openai import OpenAI
from pydantic import BaseModel
import os
import json

class AIResponse(BaseModel):
    should_comment: bool
    reason: str
    proposed_comment: str

class AIAnalyzer:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            organization=os.getenv("OPENAI_ORGANIZATION_ID"),
            project=os.getenv("OPENAI_PROJECT_ID")
        )

    def should_comment(self, thread_content) -> AIResponse:
        """Analyze a thread and decide if we should comment"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": """You are a highly selective AI advisor for the Optimism governance forum.
                    You should ONLY suggest commenting when you have specific, valuable insights that would meaningfully contribute to the discussion.

                    Criteria for commenting:
                    - You have specific technical knowledge relevant to the discussion
                    - You can provide unique perspectives that haven't been mentioned
                    - You can connect this topic to other relevant governance discussions or precedents
                    - You can clarify misconceptions with factual information

                    Do NOT comment if:
                    - The discussion is primarily opinion-based
                    - Your contribution would be generic or obvious
                    - The topic is already well-covered by existing comments
                    - You're unsure about any technical claims you'd make

                    Return a JSON object matching the Pydantic model with:
                    - should_comment: boolean
                    - reason: string explaining your decision
                    - proposed_comment: string with your comment if should_comment is true, empty string if false"""},
                    {"role": "user", "content": f"Please analyze this thread and decide if you should comment:\n\n{thread_content}"}
                ],
                response_format={ "type": "json_object" }
            )

            # Parse the JSON response into our Pydantic model
            return AIResponse.model_validate_json(response.choices[0].message.content)

        except Exception as e:
            print(f"Error in AI analysis: {e}")
            return None
