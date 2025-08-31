import json
import logging
from openai import AsyncOpenAI
from models import Course, Session, Topic
from config import Config

logger = logging.getLogger(__name__)

class CourseGenerator:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=Config.OPENAI_API_KEY)

    async def _call_llm(self, prompt: str, max_tokens: int = 800, max_retries: int = 2) -> dict:
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

                # Try parsing JSON
                return json.loads(text)

            except json.JSONDecodeError:
                logger.warning(f"LLM returned invalid JSON, retrying (attempt {attempt+1})...")
                attempt += 1
            except Exception as e:
                logger.error(f"LLM error: {e}")
                return {}

        logger.error("Failed to get valid JSON from LLM after retries")
        return {}

    async def generate_course_structure(
        self, title: str, total_sessions: int, topics_per_session: int
    ) -> Course:
        prompt = f"""
        Create a course outline for '{title}' with {total_sessions} sessions.
        Each session should have {topics_per_session} distinct topics.
        Return JSON in this format:
        {{
          "subject": "{title}",
          "level": "beginner",
          "total_sessions": {total_sessions},
          "sessions": [
            {{
              "session_no": 1,
              "session_name": "Intro to ...",
              "learning_objectives": ["..."],
              "topics": [
                {{"title": "Topic 1"}}
              ]
            }}
          ]
        }}
        """

        parsed = await self._call_llm(prompt)
        if not parsed:
            raise ValueError("❌ Failed to generate valid JSON from LLM")

        # Hydrate into Pydantic models
        sessions = []
        for s in parsed.get("sessions", []):
            topics = [
                Topic(
                    title=t.get("title", ""),
                    duration_minutes=0,  # placeholder
                    youtube_url="",
                    questions=[]
                )
                for t in s.get("topics", [])
            ]

            session = Session(
                session_no=s.get("session_no", 0),
                session_name=s.get("session_name", ""),
                learning_objectives=s.get("learning_objectives", []),
                topics=topics,
                coding_problem="",
                coding_solution=""
            )
            sessions.append(session)

        course = Course(
            subject=parsed.get("subject", title),
            level=parsed.get("level", "beginner"),
            total_sessions=parsed.get("total_sessions", total_sessions),
            sessions=sessions,
        )

        return course
