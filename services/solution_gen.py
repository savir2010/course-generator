import json
import logging
from models import ProblemSolution
import openai
from config import Config

logger = logging.getLogger(__name__)

class SolutionGen:
    def __init__(self):
        self.client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def generate_solution(
        self, problem_statement: str, skeleton_code: str
    ) -> ProblemSolution:
        prompt = f"""
        You are a Python expert.
        Given this problem statement and skeleton code, fill in the solution.
        Return valid JSON with keys: problem_statement, skeleton_code, solution_code.

        Problem Statement:
        \"\"\"{problem_statement}\"\"\"

        Skeleton Code:
        \"\"\"{skeleton_code}\"\"\"
        """

        try:
            response = await self.client.chat.completions.create(
                model=Config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful Python coding assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0
            )

            raw_text = response.choices[0].message.content.strip()

            # Remove code fences if present
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()

            data = json.loads(raw_text)
            return ProblemSolution(**data)

        except Exception as e:
            logger.error(f"Failed to generate solution: {e}")
            return ProblemSolution(
                problem_statement=problem_statement,
                skeleton_code=skeleton_code,
                solution_code="# Unable to generate solution"
            )
