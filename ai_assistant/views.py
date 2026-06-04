from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from google import genai
from google.genai import types
import os

# Initialize GenAI Client using settings or env variable
api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
client = None
if api_key:
    client = genai.Client(api_key=api_key)

@login_required
def ai_assistant(request):
    return render(request, 'ai_assistant/chat.html')

@csrf_exempt
@login_required
def ai_query(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        prompt = data.get('prompt', '')
        if not prompt:
            return JsonResponse({'error': 'No prompt provided'}, status=400)
        
        # Instantiate client lazily or check if client exists
        # In case the key is added to .env after startup
        global client
        if not client:
            current_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
            if current_key:
                client = genai.Client(api_key=current_key)
        
        if not client:
            return JsonResponse({'error': 'Edmond AI API key is not configured. Please add GEMINI_API_KEY to your .env file.'}, status=500)
            
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=(
                        "You are Edmond AI, a friendly, encouraging, and highly knowledgeable academic tutor "
                        "and study assistant for university students. You help students understand complex academic "
                        "topics, summarize study material, outline essays, draft study plans, and write or debug code. "
                        "Keep your responses structured, clear, and easy to read. Use Markdown, lists, and code blocks "
                        "where appropriate to make information accessible."
                    ),
                    max_output_tokens=1500,
                    temperature=0.7,
                )
            )
            answer = response.text
            return JsonResponse({'answer': answer})
        except Exception as e:
            error_str = str(e)
            
            # Provide user-friendly error messages
            if '503' in error_str or 'UNAVAILABLE' in error_str:
                error_msg = 'Edmond AI is currently experiencing high demand. Please try again in a moment.'
            elif '401' in error_str or 'UNAUTHENTICATED' in error_str:
                error_msg = 'API key configuration error. Please check your GEMINI_API_KEY in .env file.'
            elif '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str:
                error_msg = 'Rate limit exceeded. Please wait a moment before sending another message.'
            elif '400' in error_str or 'INVALID_ARGUMENT' in error_str:
                error_msg = 'Invalid request. Please rephrase your question and try again.'
            else:
                error_msg = 'An error occurred while processing your request. Please try again.'
            
            return JsonResponse({'error': error_msg}, status=500)
    return JsonResponse({'error': 'Method not allowed'}, status=405)