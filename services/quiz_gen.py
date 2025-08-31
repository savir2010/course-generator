import json
import logging
from typing import List
from openai import AsyncOpenAI
from config import Config
from models import TopicQuestion  # your Pydantic model

logger = logging.getLogger(__name__)

class QuizGen:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def _call_llm(self, prompt: str, max_tokens: int = 500, max_retries: int = 2) -> List[dict]:
        attempt = 0
        while attempt <= max_retries:
            try:
                response = await self.client.chat.completions.create(
                    model=Config.MODEL_NAME,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )

                text = response.choices[0].message.content.strip()

                # Strip code fences if present
                if text.startswith("```"):
                    text = "\n".join(text.splitlines()[1:])
                    if text.endswith("```"):
                        text = "\n".join(text.splitlines()[:-1])

                return json.loads(text)

            except json.JSONDecodeError:
                logger.warning(f"LLM returned invalid JSON, retrying (attempt {attempt+1})...")
                attempt += 1
            except Exception as e:
                logger.error(f"LLM error: {e}")
                return []

        logger.error("Failed to get valid JSON from LLM after retries")
        return []

    async def generate_quiz(self, video_title: str, duration_minutes: int) -> List[TopicQuestion]:
        num_questions = max(1, duration_minutes // 5)  # at least 1 question
        prompt = f"""
        Generate {num_questions} multiple choice questions for the YouTube video '{video_title}'.
        Each question should have 4 options and specify the correct answer.
        Return a valid JSON list matching this format:
        [
            {{
                "question": "What is the main topic?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A"
            }}
        ]
        """

        questions_data = await self._call_llm(prompt)

        if not questions_data:
            # fallback if LLM fails
            questions_data = [
                {
                    "question": f"What is the main concept of '{video_title}'?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A"
                }
            ]

        # Hydrate into Pydantic models
        questions = []
        for q in questions_data:
            try:
                questions.append(TopicQuestion(**q))
            except Exception as e:
                logger.warning(f"Failed to parse question: {q}, error: {e}")

        return questions
