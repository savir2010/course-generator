from fastapi import FastAPI
from services.course_gen import CourseGenerator
from services.topic_gen import TopicGen
from services.quiz_gen import QuizGen
from services.transcript_gen import TranscriptGen
from services.homework_gen import HomeworkGen
from services.solution_gen import SolutionGen

app = FastAPI(title="Course Generator API", version="2.0.0")

course_gen = CourseGenerator()
topic_gen = TopicGen()
quiz_gen = QuizGen()
transcript_gen = TranscriptGen()
homework_gen = HomeworkGen()
solution_gen = SolutionGen()

@app.get("/")
async def root():
    return {"message": "Course Generator API v2"}

@app.post("/course")
async def make_course(title: str, sessions: int, topics: int):
    return await course_gen.generate_course_structure(title, sessions, topics)

@app.get("/video")
async def find_video(topic: str):
    return await topic_gen.get_video(topic)

@app.post("/quiz")
async def make_quiz(title: str, duration: int):
    return await quiz_gen.generate_quiz(title, duration)

@app.post("/transcript")
async def get_transcript(url: str):
    return transcript_gen.generate_transcript(url)

@app.post("/homework")
async def make_homework(transcript: str):
    return await homework_gen.generate_homework(transcript)

@app.post("/solution")
async def make_solution(problem: str, skeleton: str):
    return await solution_gen.generate_solution(problem, skeleton)