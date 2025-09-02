# Course Generator MCP Server

A Model Context Protocol (MCP) server that provides comprehensive course generation capabilities including course structure creation, video content discovery, quiz generation, transcript processing, and homework assignment creation.

## Features

-  **Course Structure Generation**: Create complete course outlines with sessions and topics
-  **Video Content Discovery**: Find relevant educational videos for any topic
-  **Quiz Generation**: Generate timed quizzes with multiple choice and open-ended questions
-  **Transcript Processing**: Extract transcripts from video URLs
-  **Homework Generation**: Create assignments based on video transcripts
-  **Solution Generation**: Generate solutions for coding problems with skeleton code

## Prerequisites

- Python 3.8 or higher
- Claude Desktop application
- OpenAI API key
- SerpAPI key (for web search functionality)

## Installation

### 1. Clone or Download the Project

```bash
git clone <your-repository-url>
cd <project-directory>
```

### 2. Create Virtual Environment

Create and activate a Python virtual environment in the project directory:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root directory:

```bash
touch .env
```

Add your API keys to the `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here
```

### 5. Configure Claude Desktop

#### Step 1: Open Claude Desktop Configuration

1. Open Claude Desktop application
2. Go to **Profile Settings** (click your profile icon)
3. Navigate to **Developer** tab
4. Click **Edit Config**

#### Step 2: Update Configuration

Replace the existing configuration with the following (update the paths to match your system):

```json
{
  "mcpServers": {
    "course-generator": {
      "command": "/path/to/your/project/venv/bin/python",
      "args": [
        "/path/to/your/project/course_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/project"
      }
    }
  }
}
```

**Important**: Replace `/path/to/your/project` with the actual path to your project directory.

#### Example Configuration:

```json
{
  "mcpServers": {
    "course-generator": {
      "command": "/Users/username/projects/course-generator/venv/bin/python",
      "args": [
        "/Users/username/projects/course-generator/course_mcp.py"
      ],
      "env": {
        "PYTHONPATH": "/Users/username/projects/course-generator"
      }
    }
  }
}
```

### 6. Restart Claude Desktop

After saving the configuration:
1. Close Claude Desktop completely
2. Reopen Claude Desktop
3. The MCP server should now be available

## Usage

Once configured, you can use the following functions in Claude Desktop:

### Generate Course Structure
```
Generate a course on "Introduction to Machine Learning" with 8 sessions and 3 topics per session
```

### Find Educational Videos
```
Find videos about "neural networks basics"
```

### Create Quizzes
```
Generate a 15-minute quiz on "Python fundamentals"
```

### Get Video Transcripts
```
Get transcript from this video: https://youtube.com/watch?v=example
```

### Generate Homework
```
Create homework assignments based on this transcript: [transcript content]
```

### Generate Solutions
```
Generate a solution for this problem: "Create a sorting algorithm" with this skeleton code: [code template]
```

## Available Functions

| Function | Description | Parameters |
|----------|-------------|------------|
| `generate_course` | Creates complete course structure | `title`, `sessions`, `topics` |
| `find_video` | Searches for educational videos | `topic` |
| `generate_quiz` | Creates timed quizzes | `title`, `duration` |
| `get_transcript` | Extracts video transcripts | `url` |
| `generate_homework` | Creates homework from transcripts | `transcript` |
| `generate_solution` | Generates code solutions | `problem`, `skeleton` |
