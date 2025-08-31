import json
import logging
from typing import List
from models import HomeworkProblem
import openai
from config import Config

logger = logging.getLogger(__name__)

class HomeworkGen:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def generate_homework(self, transcript: str) -> List[HomeworkProblem]:
        prompt = f"""
        You are an educational assistant. Based on the following transcript:
        \"\"\"{transcript}\"\"\"
        
        Generate **1 Python homework problem** related to the main concepts. 
        Include:
        1. Problem statement (like a LeetCode description)
        2. Python skeleton code with function signature
        3. 3-5 hints guiding the student to solve it
        
        Return valid JSON like this:
        [
          {{
            "problem_statement": "Write a function to ...",
            "skeleton_code": "def my_function(...):\\n    pass",
            "hints": ["Hint 1", "Hint 2", "Hint 3"]
          }}
        ]
        """

        try:
            response = await self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are an expert educational assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )

            raw_text = response.choices[0].message.content.strip()

            # Remove code fences if present
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()

            data = json.loads(raw_text)

            # Hydrate Pydantic models
            homework_problems = [HomeworkProblem(**p) for p in data]
            return homework_problems

        except Exception as e:
            logger.error(f"Failed to generate homework: {e}")

