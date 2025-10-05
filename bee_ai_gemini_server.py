#!/usr/bin/env python3
"""
Bee AI - Gemini API Integration
Uses Google Gemini API for bee-related Q&A with fine-tuned responses
"""

import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging

# Import API key from config
try:
    from config import GEMINI_API_KEY
except ImportError:
    GEMINI_API_KEY = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global variables
model = None
knowledge_base = None

def load_knowledge_base():
    """Load bee knowledge base from JSONL file"""
    global knowledge_base
    knowledge_base = []
    
    try:
        with open('bee_ai_training_data.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    knowledge_base.append(data)
        
        logger.info(f"Loaded {len(knowledge_base)} knowledge entries")
        return True
        
    except Exception as e:
        logger.error(f"Error loading knowledge base: {str(e)}")
        return False

def initialize_gemini():
    """Initialize Gemini API"""
    global model
    
    try:
        # Get API key from config file, environment variable, or Vercel env
        api_key = GEMINI_API_KEY or os.getenv('GEMINI_API_KEY') or os.getenv('VERCEL_GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not found in config.py, environment variables, or Vercel env")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        logger.info("Gemini API initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing Gemini: {str(e)}")
        return False

def find_relevant_knowledge(question):
    """Find relevant knowledge entries for the question"""
    if not knowledge_base:
        return []
    
    question_lower = question.lower()
    relevant_entries = []
    
    # Enhanced keyword matching with synonyms and related terms
    keywords = question_lower.split()
    
    # Add synonyms and related terms
    keyword_expansions = {
        'daisies': ['daisy', 'bellis', 'marguerite', 'oxeye'],
        'grow': ['growing', 'cultivate', 'plant', 'planting', 'cultivation'],
        'best': ['optimal', 'ideal', 'perfect', 'excellent', 'suitable'],
        'where': ['location', 'place', 'region', 'area', 'country'],
        'bees': ['bee', 'honeybee', 'pollinator', 'pollination'],
        'honey': ['nectar', 'honey production', 'honey yield'],
        'bloom': ['blooming', 'flowering', 'blossom', 'blossoming'],
        'season': ['time', 'period', 'when', 'timing']
    }
    
    # Expand keywords
    expanded_keywords = set(keywords)
    for keyword in keywords:
        if keyword in keyword_expansions:
            expanded_keywords.update(keyword_expansions[keyword])
    
    for entry in knowledge_base:
        user_content = entry['messages'][0]['content'].lower()
        assistant_content = entry['messages'][1]['content'].lower()
        combined_content = user_content + " " + assistant_content
        
        # Check for keyword matches with scoring
        score = 0
        for keyword in expanded_keywords:
            if keyword in user_content:
                score += 3  # Higher score for question matches
            if keyword in assistant_content:
                score += 2  # Medium score for answer matches
            if keyword in combined_content:
                score += 1  # Lower score for any match
        
        # Check for partial matches
        for keyword in expanded_keywords:
            if len(keyword) > 3:  # Only for longer keywords
                for word in combined_content.split():
                    if keyword in word or word in keyword:
                        score += 0.5
        
        if score > 0:
            relevant_entries.append((entry, score))
    
    # Sort by relevance score
    relevant_entries.sort(key=lambda x: x[1], reverse=True)
    
    # Return top 5 most relevant entries (increased from 3)
    return [entry[0] for entry in relevant_entries[:5]]

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
        logger.error(f"Error generating Gemini response: {str(e)}")
        return "I apologize, but I encountered an error processing your question. Please try again."

@app.route('/')
def index():
    """Serve the main HTML file"""
    return send_from_directory('.', 'index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        logger.info(f"Received question: {question}")
        
        # Generate response using Gemini
        response = generate_response_with_gemini(question)
        
        logger.info(f"Generated response: {response[:100]}...")
        
        return jsonify({
            'question': question,
            'answer': response,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gemini_loaded': model is not None,
        'knowledge_base_loaded': knowledge_base is not None,
        'knowledge_entries': len(knowledge_base) if knowledge_base else 0
    })

@app.route('/api/knowledge', methods=['GET'])
def get_knowledge_stats():
    """Get knowledge base statistics"""
    if not knowledge_base:
        return jsonify({'error': 'Knowledge base not loaded'}), 500
    
    return jsonify({
        'total_entries': len(knowledge_base),
        'status': 'loaded'
    })

if __name__ == '__main__':
    # Load knowledge base
    if not load_knowledge_base():
        logger.error("Failed to load knowledge base. Exiting.")
        exit(1)
    
    # Initialize Gemini
    if not initialize_gemini():
        logger.error("Failed to initialize Gemini API. Exiting.")
        exit(1)
    
    logger.info("Starting Bee AI Server with Gemini API...")
    
    # For Vercel deployment
    if os.getenv('VERCEL'):
        # Vercel environment
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
    else:
        # Local development
        app.run(host='0.0.0.0', port=5000, debug=True)
