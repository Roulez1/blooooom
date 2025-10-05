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
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
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
    """Generate response using Gemini API with knowledge base fine-tuning"""
    global model, knowledge_base
    
    try:
        # Check if model is initialized
        if model is None:
            print("Model not initialized")
            return "I apologize, but the AI service is currently unavailable. Please try again later."
        
        # Find relevant knowledge from training data
        relevant_knowledge = find_relevant_knowledge(question)
        
        # Build comprehensive prompt with training examples
        prompt = f"""You are Bee AI, an expert assistant trained on beekeeping data from BloomWatch 2025 and GBIF 2025 databases.

Your expertise includes:
- Plant phenology and flowering times across Europe
- Beekeeping practices and hive management
- Honey production timing and techniques
- Bee biology and behavior
- Climate effects on plants and bees

Training Examples (use these as reference for style and information):
"""
        
        # Add relevant training examples
        if relevant_knowledge and len(relevant_knowledge) > 0:
            for entry in relevant_knowledge[:3]:  # Use top 3 most relevant
                user_q = entry['messages'][0]['content']
                assistant_a = entry['messages'][1]['content']
                prompt += f"\nExample Q: {user_q}\nExample A: {assistant_a}\n"
        
        prompt += f"""

Now answer this question in the same style:
Question: {question}

Instructions:
1. Always respond in English only, regardless of question language
2. Use the training examples above as reference for style and data sources (BloomWatch 2025, GBIF 2025)
3. If the question is similar to training examples, use that information
4. If the question is different, use your general knowledge about bees, plants, and beekeeping
5. Be conversational, helpful, and informative
6. Keep responses concise (2-4 sentences) unless detail is requested
7. For greetings, respond warmly as Bee AI
8. You can answer ANY bee, plant, or nature-related question

Answer:"""

        # Generate response
        response = model.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            print("Empty response from Gemini")
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
        
    except Exception as e:
        print(f"Error generating Gemini response: {str(e)}")
        return "I apologize, but I encountered an error processing your question. Please try again."

# Fallback function removed - using only Gemini AI responses

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
