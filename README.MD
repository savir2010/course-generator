# Course Generator API
## Installation

Clone the repository and navigate to the folder.

## Install dependencies:
pip install -r requirements.txt

## Run the API:
uvicorn main:app --reload

## Open Swagger UI at:
http://127.0.0.1:8000/docs

# Endpoints
## POST /course

## Query Parameters:

title (string) – Title of the course

sessions (integer) – Number of sessions

topics (integer) – Number of topics per session

## GET /video

## Query Parameters:

topic (string) – Topic title

## POST /quiz

## Query Parameters:

title (string) – Video title

duration (integer) – Video duration in minutes

## POST /transcript

## Query Parameters:

url (string) – YouTube video URL

## POST /homework

## Query Parameters:

transcript (string) – Transcript of the video

## POST /solution

## Query Parameters:

problem (string) – Homework problem statement

skeleton (string) – Skeleton code for the problem