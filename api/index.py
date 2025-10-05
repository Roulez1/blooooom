#!/usr/bin/env python3
"""
Bee AI - Vercel Serverless Function
Simplified version for Vercel deployment
"""

import os
import json
import google.generativeai as genai
from http.server import BaseHTTPRequestHandler
import urllib.parse

# Global variables
knowledge_base = []
model = None

def load_knowledge_base():
    """Load knowledge base from JSONL file"""
    global knowledge_base
    
    try:
        knowledge_base = []
        
        # Try to load the JSONL file from multiple possible locations
        jsonl_candidates = [
            'bee_ai_training_data.jsonl',
            '../bee_ai_training_data.jsonl',
            os.path.join(os.path.dirname(__file__), '..', 'bee_ai_training_data.jsonl'),
            os.path.join(os.getcwd(), 'bee_ai_training_data.jsonl')
        ]
        
        jsonl_loaded = False
        for jsonl_path in jsonl_candidates:
            if os.path.exists(jsonl_path):
                try:
                    with open(jsonl_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                entry = json.loads(line.strip())
                                knowledge_base.append(entry)
                    jsonl_loaded = True
                    print(f"Loaded knowledge base from: {jsonl_path}")
                    break
                except Exception as e:
                    print(f"Error loading {jsonl_path}: {str(e)}")
                    continue
        
        if not jsonl_loaded:
            # Fallback: create a minimal knowledge base
            print("Using fallback knowledge base")
            knowledge_base = [
                {
                    "messages": [
                        {"role": "user", "content": "When does wild garlic bloom in Germany?"},
                        {"role": "assistant", "content": "Wild garlic typically blooms from late March to early May in central Germany. Based on BloomWatch forecasts and GBIF 2025 records, you should move your hives in early April to align with peak nectar flow."}
                    ]
                },
                {
                    "messages": [
                        {"role": "user", "content": "When does clover bloom in Turkey?"},
                        {"role": "assistant", "content": "I am unable to provide information about clover blooming times in Turkey, as my knowledge is restricted to European countries and regions. However, in northern Spain, BloomWatch 2025 satellite data shows clover blooming from mid-April through June."}
                    ]
                },
                {
                    "messages": [
                        {"role": "user", "content": "What's the best period for honey collection in southern Spain?"},
                        {"role": "assistant", "content": "According to GBIF 2025 data, sunflowers in southern Spain reach full bloom between late June and August. Start honey collection in mid-July when nectar availability peaks."}
                    ]
                }
            ]
        
        return True
        
    except Exception as e:
        print(f"Error loading knowledge base: {str(e)}")
        return False

def initialize_gemini():
    """Initialize Gemini API"""
    global model
    
    try:
        # Get API key from environment variable
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("GEMINI_API_KEY environment variable not set")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("Gemini API initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing Gemini: {str(e)}")
        return False

def find_relevant_knowledge(question):
    """Find relevant knowledge entries for the question"""
    if not knowledge_base:
        return []
    
    question_lower = question.lower()
    relevant_entries = []
    
    # Simple keyword matching
    keywords = question_lower.split()
    
    for entry in knowledge_base:
        user_content = entry['messages'][0]['content'].lower()
        assistant_content = entry['messages'][1]['content'].lower()
        combined_content = user_content + " " + assistant_content
        
        # Check for keyword matches
        score = 0
        for keyword in keywords:
            if keyword in user_content:
                score += 3
            if keyword in assistant_content:
                score += 2
            if keyword in combined_content:
                score += 1
        
        if score > 0:
            relevant_entries.append((entry, score))
    
    # Sort by relevance score
    relevant_entries.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 3 most relevant entries
    return [entry[0] for entry in relevant_entries[:3]]

def generate_response_with_gemini(question):
    """Generate response using Gemini API with knowledge base context"""
    global model
    
    try:
        # Find relevant knowledge
        relevant_knowledge = find_relevant_knowledge(question)
        
        # Build context prompt
        context_prompt = """You are Bee AI, a friendly and helpful assistant specialized in bee behavior, plant phenology, and honey production. 
You can answer questions about bees, plants, honey production, and general beekeeping topics.

IMPORTANT: 
- For bee-related questions, use ONLY the provided knowledge base
- For general greetings and casual conversation, respond naturally and friendly
- If asked about topics not in your knowledge base, provide helpful information BUT ONLY about EUROPEAN countries and regions
- You are restricted to European knowledge only - do not provide information about other continents

Knowledge Base Context:
"""
        
        # Add relevant knowledge entries only if there are any
        if relevant_knowledge:
            for entry in relevant_knowledge:
                user_q = entry['messages'][0]['content']
                assistant_a = entry['messages'][1]['content']
                context_prompt += f"\nQ: {user_q}\nA: {assistant_a}\n"
        
        context_prompt += f"""

User Question: {question}

Instructions:
1. If this is a greeting (hello, hi, etc.), respond warmly and introduce yourself as Bee AI
2. If this is a bee-related question, answer ONLY based on the knowledge base provided above
3. If the question is about plants/flowers/animals/beekeeping NOT in the knowledge base, provide helpful information using your own knowledge BUT RESTRICT to EUROPEAN countries and regions only
4. If the question is not covered in the knowledge base, provide helpful information using your own knowledge but RESTRICT your knowledge to EUROPEAN countries and regions only
5. For general conversation, be friendly and helpful while steering toward bee topics when appropriate
6. Provide detailed, scientific answers with specific data when available from the knowledge base
7. Include relevant dates, locations, and scientific references when mentioned in the knowledge base
8. IMPORTANT: Never provide information about non-European countries or regions
9. CRITICAL: Keep your responses SHORT and CONCISE - maximum 2-3 sentences unless specifically asked for detailed information
10. DO NOT introduce yourself or mention "Bee AI" in responses unless it's a greeting - just answer the question directly
11. USE YOUR OWN KNOWLEDGE: For topics not in the knowledge base, use your general knowledge about European plants, animals, and beekeeping

Answer:"""

        # Generate response
        response = model.generate_content(context_prompt)
        
        return response.text.strip()
        
    except Exception as e:
        print(f"Error generating Gemini response: {str(e)}")
        return "I apologize, but I encountered an error processing your question. Please try again."

# Initialize on module load
if not load_knowledge_base():
    print("Failed to load knowledge base")
if not initialize_gemini():
    print("Failed to initialize Gemini API")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'gemini_loaded': model is not None,
                'knowledge_base_loaded': len(knowledge_base) > 0,
                'knowledge_entries': len(knowledge_base)
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/chat':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                question = data.get('question', '').strip()
                
                if not question:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'No question provided'}).encode())
                    return
                
                # Generate response using Gemini
                response_text = generate_response_with_gemini(question)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'question': question,
                    'answer': response_text,
                    'status': 'success'
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"Error in chat endpoint: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Internal server error'}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
