#!/usr/bin/env python3
"""
Course Generator MCP Server
Provides course generation, video finding, quiz creation, and related educational tools to Claude.
"""
from pydantic import BaseModel
import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, 
    Tool, 
    TextContent, 
    ImageContent, 
    EmbeddedResource,
    LoggingLevel
)

# Import your existing services
from services.course_gen import CourseGenerator
from services.topic_gen import TopicGen
from services.quiz_gen import QuizGen
from services.transcript_gen import TranscriptGen
from services.homework_gen import HomeworkGen
from services.solution_gen import SolutionGen

# Initialize the MCP server
server = Server("course-generator")

# Initialize your service classes
course_gen = CourseGenerator()
topic_gen = TopicGen()
quiz_gen = QuizGen()
transcript_gen = TranscriptGen()
homework_gen = HomeworkGen()
solution_gen = SolutionGen()

def to_json(obj: Any) -> str:
    """Recursively convert Pydantic models, lists, and dicts into JSON string."""
    if isinstance(obj, BaseModel):
        return json.dumps(_to_dict_recursive(obj), indent=2)
    elif isinstance(obj, list):
        return json.dumps([_to_dict_recursive(o) for o in obj], indent=2)
    elif isinstance(obj, dict):
        return json.dumps({k: _to_dict_recursive(v) for k, v in obj.items()}, indent=2)
    else:
        return json.dumps(str(obj), indent=2)  # fallback

def _to_dict_recursive(obj: Any):
    if isinstance(obj, BaseModel):
        return {k: _to_dict_recursive(v) for k, v in obj.dict().items()}
    elif isinstance(obj, list):
        return [_to_dict_recursive(o) for o in obj]
    elif isinstance(obj, dict):
        return {k: _to_dict_recursive(v) for k, v in obj.items()}
    else:
        return obj


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools for course generation."""
    return [
        Tool(
            name="generate_course",
            description="Generate a complete course structure with sessions and topics",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the course to generate"
                    },
                    "sessions": {
                        "type": "integer",
                        "description": "Number of sessions in the course",
                        "minimum": 1
                    },
                    "topics": {
                        "type": "integer", 
                        "description": "Number of topics per session",
                        "minimum": 1
                    }
                },
                "required": ["title", "sessions", "topics"]
            }
        ),
        Tool(
            name="find_video",
            description="Find educational videos related to a specific topic",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to find videos for"
                    }
                },
                "required": ["topic"]
            }
        ),
        Tool(
            name="generate_quiz",
            description="Generate a quiz for a given topic with specified duration",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title/topic of the quiz"
                    },
                    "duration": {
                        "type": "integer",
                        "description": "Duration of the quiz in minutes",
                        "minimum": 5
                    }
                },
                "required": ["title", "duration"]
            }
        ),
        Tool(
            name="get_transcript",
            description="Generate transcript from a video URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the video to transcribe",
                        "format": "uri"
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="generate_homework",
            description="Generate homework assignments based on a transcript",
            inputSchema={
                "type": "object",
                "properties": {
                    "transcript": {
                        "type": "string",
                        "description": "The transcript to base homework on"
                    }
                },
                "required": ["transcript"]
            }
        ),
        Tool(
            name="generate_solution",
            description="Generate solution for a problem with given skeleton code",
            inputSchema={
                "type": "object",
                "properties": {
                    "problem": {
                        "type": "string",
                        "description": "Description of the problem to solve"
                    },
                    "skeleton": {
                        "type": "string",
                        "description": "Skeleton code or template for the solution"
                    }
                },
                "required": ["problem", "skeleton"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls from Claude."""
    
    try:
        if name == "generate_course":
            title = arguments["title"]
            sessions = arguments["sessions"]
            topics = arguments["topics"]
            
            result = await course_gen.generate_course_structure(title, sessions, topics)
            course_dict = result.dict()  # Convert Pydantic model to dict
            course_json = json.dumps(course_dict, indent=2)
            response_data = {
                "quiz_data": course_json,
                "instructions": "This is structured a course. Present as plain text or markdown list format only. Do not create HTML artifacts or interactive elements.",
                "format_preference": "text_only"
            }

            return [TextContent(
                type="text",
                text=json.dumps(response_data, indent=2)  # Now properly serializable
            )]


        elif name == "find_video":
            topic = arguments["topic"]
            result = await topic_gen.get_video(topic)
            return [TextContent(
                type="text", 
                text=json.dumps(result, indent=2)
            )]
            
        elif name == "generate_quiz":
            title = arguments["title"]
            duration = arguments["duration"]
            result = await quiz_gen.generate_quiz(title, duration)
            
            # Convert list of Pydantic TopicQuestion objects to list of dicts
            result_list = [q.dict() for q in result]
            response_data = {
                "quiz_data": result_list,
                "instructions": "This is structured quiz data. Present as plain text or markdown list format only. Do not create HTML artifacts or interactive elements.",
                "format_preference": "text_only"
            }

            return [TextContent(
                type="text",
                text=json.dumps(response_data, indent=2)  # Now properly serializable
            )]


        elif name == "get_transcript":
            url = arguments["url"]
            result = transcript_gen.generate_transcript(url)
            if asyncio.iscoroutine(result):
                result = await result
            
            transcript_text = str(result).strip() if result else ""
            
            response_data = {
                "transcript": transcript_text,
                "status": "success" if transcript_text else "failed",
                "message": "Transcript generated successfully" if transcript_text else "Failed to generate transcript"
            }
            
            return [TextContent(
                type="text", 
                text=json.dumps(response_data, indent=2)
            )]
            


        elif name == "generate_homework":
            transcript = arguments["transcript"]
            result = await homework_gen.generate_homework(transcript)
            homework_json = to_json(result)
            return [TextContent(type="text", text=homework_json)]

        elif name == "generate_solution":
            problem = arguments["problem"]
            skeleton = arguments["skeleton"]
            result = await solution_gen.generate_solution(problem, skeleton)
            solution_json = to_json(result)
            return [TextContent(type="text", text=solution_json)]

        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources."""
    return [
        Resource(
            uri="course://info",
            name="Course Generator Information",
            description="Information about the course generator capabilities",
            mimeType="text/plain"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content."""
    if uri == "course://info":
        return """Course Generator MCP Server

This server provides educational content generation tools:

1. generate_course: Create structured course outlines with sessions and topics
2. find_video: Search for educational videos on specific topics  
3. generate_quiz: Create quizzes with time limits
4. get_transcript: Extract transcripts from video URLs
5. generate_homework: Generate homework from transcripts
6. generate_solution: Provide solutions for coding problems

All tools return structured JSON responses for easy integration.
"""
    else:
        raise ValueError(f"Unknown resource: {uri}")

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, 
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())