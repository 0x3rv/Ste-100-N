import os
from typing import List, Dict, Any
from langchain.agents import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from googleapiclient.discovery import build
from langchain.tools import StructuredTool
from app.models.user import Chat, chat_collection

from pydantic import BaseModel

class AdvancedRecommendPlaylistArgs(BaseModel):
    query: str
    count: int = 5

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

def search_youtube_song(query: str) -> Dict[str, Any]:
    try:
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=1,
            type='video'
        ).execute()
        
        if not search_response['items']:
            return {"title": "Error", "code": "No results found"}
        
        video_id = search_response['items'][0]['id']['videoId']
        title = search_response['items'][0]['snippet']['title']
        
        return {"title": title, "code": video_id}
    except Exception as e:
        return {"title": "Error", "code": str(e)}

def search_youtube_playlist(songs: List[str]) -> List[Dict[str, Any]]:
    return [search_youtube_song(song) for song in songs]

def advanced_recommend_song(query: str) -> Dict[str, Any]:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""Recommend ONE perfect song based on this query: "{query}".
        Consider mood, genre, artist preferences, and any other specifics mentioned.
        Return ONLY 'Song Name by Artist'."""
        
        response = model.generate_content(prompt)
        song_recommendation = response.text.strip()
        return search_youtube_song(song_recommendation)
    except Exception as e:
        return {"title": "Error", "code": str(e)}

def advanced_recommend_playlist(query: str, count: int = 5) -> List[Dict[str, Any]]:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""Create a playlist of {count} songs based on this query: "{query}".
        Consider mood, genre, artist preferences, and any other specifics mentioned.
        Return each as 'Song Name by Artist' in a numbered list.
        IMPORTANT: Dont give any extra lines just name Song Name by Artist.
        """
        
        response = model.generate_content(prompt)
        songs = [line.split('. ')[-1] for line in response.text.strip().split('\n') if line.strip()]
        return search_youtube_playlist(songs)
    except Exception as e:
        return [{"title": "Error", "code": str(e)}]
    

tools = [
    Tool(
        name="AdvancedRecommendSong",
        func=advanced_recommend_song,
        description="Recommends a song based on any music query including mood, genre, artist preferences."
    ),
    Tool(
        name="AdvancedRecommendPlaylist",
        func=advanced_recommend_playlist,
        description="Recommends a playlist based on any music query including mood, genre, artist preferences."
    )
]

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

prompt = PromptTemplate.from_template("""
System: You are a specialized music recommendation system.

IMPORTANT: 
1. Your final output must ONLY contain RAW JSON - no additional text or formatting
2. NEVER use markdown code blocks in your response
3. If the tool returns a single song, wrap it in an array [{{"title": "Song", "code":"code"}}]
4. For non-music questions, return exactly {{"DomainError": "I only answer music-related questions"}}"

You have access to the following tools:
{tools}

Use this exact format:
Question: the input question you must answer
Thought: your reasoning process (not in final output)
Action: the tool name, must be one of [{tool_names}]
Action Input: the input for the tool
Observation: the result from the tool
... (this Thought/Action/Action Input/Observation can repeat)
Thought: I now know the final answer
Final Answer: ONLY THE RAW JSON DATA, NO CODE BLOCKS, NO EXPLANATIONS

Begin!

Question: {input}
{agent_scratchpad}
""")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10, 
    max_execution_time=60
)

async def process_user_query(query: str, user_email: str):
    try:
        # Call the agent executor with properly formatted input
        # The input should be a string, not a dict with "query" key
        result = agent_executor.invoke({"input": query})
        
        print(result)
        
        # Store the chat in MongoDB
        response_text = result.get("output", str(result))
        chat = Chat(
            user_email=user_email,
            prompt=query,
            response=response_text
        )
        await chat_collection.insert_one(chat.model_dump())
        
        return result
    except Exception as e:
        error_result = [{"title": "Error", "code": str(e)}]       
        return error_result

