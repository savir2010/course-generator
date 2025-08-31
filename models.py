from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

class ProblemSolution(BaseModel):
    problem_statement: str
    skeleton_code: str
    solution_code: str
    
class HomeworkProblem(BaseModel):
    problem_statement: str      
    skeleton_code: str          
    hints: List[str]            

class TopicQuestion(BaseModel):
    question: str
    options: List[str]
    correct_answer: str

class Topic(BaseModel):
    title: str
    duration_minutes: int
    youtube_url: str
    questions: List[TopicQuestion]

class Session(BaseModel):
    session_no: int
    session_name: str
    learning_objectives: List[str]
    topics: List[Topic]
    coding_problem: str
    coding_solution: str

class Course(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    subject: str
    level: str
    total_sessions: int
    sessions: List[Session]
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
