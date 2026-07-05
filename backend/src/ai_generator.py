import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from typing import Dict, Any

client = None

load_dotenv(Path(__file__).resolve().parent / ".env")
def _get_client():
    global client
    if client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        client = OpenAI(api_key=api_key)
    return client

def generate_challenge_with_ai(difficulty: str) -> Dict[str, any]:
    system_prompt = """You are an expert coding challenge creator. 
    Your task is to generate a coding question with multiple choice answers.
    The question should be appropriate for the specified difficulty level.

    For easy questions: Focus on basic syntax, simple operations, or common programming concepts.
    For medium questions: Cover intermediate concepts like data structures, algorithms, or language features.
    For hard questions: Include advanced topics, design patterns, optimization techniques, or complex algorithms.

    Return the challenge in the following JSON structure:
    {
        "title": "The question title",
        "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
        "correct_answer_id": 0, // Index of the correct answer (0-3)
        "explanation": "Detailed explanation of why the correct answer is right"
    }

    Make sure the options are plausible but with only one clearly correct answer.
    """
    try: 
        client_instance = _get_client()
        response = client_instance.chat.completions.create(
            model = "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Generate a {difficulty} difficulty coding challenge."}
            ],
            response_format={"type": "json_object"},
            temperature = 0.7
        )

        # Defensive extraction of the model content (supports dict or string responses)
        raw_choice = None
        try:
            raw_choice = response.choices[0]
        except Exception:
            try:
                raw_choice = response["choices"][0]
            except Exception:
                raw_choice = None

        content = None
        if raw_choice is not None:
            # message may be an object with attributes or a dict
            msg = None
            try:
                msg = getattr(raw_choice, "message", None)
            except Exception:
                try:
                    msg = raw_choice.get("message")
                except Exception:
                    msg = None

            if msg:
                if isinstance(msg, dict):
                    content = msg.get("content")
                else:
                    content = getattr(msg, "content", None)

            if content is None:
                # fallback common fields
                content = getattr(raw_choice, "text", None) or (raw_choice.get("text") if isinstance(raw_choice, dict) else None)

        if content is None:
            raise ValueError("No content returned from model")

        # If the SDK already parsed JSON into a dict/list, use it directly
        if isinstance(content, (dict, list)):
            challenge_data = content
        else:
            s = content.strip() if isinstance(content, str) else content
            # remove fenced code blocks if present
            if isinstance(s, str) and s.startswith("```"):
                # try to extract inner block
                parts = s.split("```")
                if len(parts) >= 3:
                    s = "".join(parts[1:-1]).strip()

            # attempt to extract JSON object substring if there's surrounding text
            if isinstance(s, str):
                first = s.find("{")
                last = s.rfind("}")
                json_str = s[first:last+1] if (first != -1 and last != -1 and last > first) else s
                challenge_data = json.loads(json_str)

        required_fields = ["title", "options", "correct_answer_id", "explanation"]
        for field in required_fields:
            if field not in challenge_data:
                raise ValueError(f"Missing required field: {field}")
        return challenge_data
    
    except Exception as e:
        print(e)
        return{
            "title": "Basic Python List Operation",
            "options": [
                "my_list.append(5)",
                "my_list.add(5)",
                "my_list.push(5)",
                "my_list.insert(5)",
            ],
            "correct_answer_id": 0,
            "explanation": "In Python, append() is the correct method to add an element to the end of a list. "
        }

