#!/usr/bin/env python3
"""
Bee AI - Gemini API Integration for Vercel
Uses Google Gemini API for bee-related Q&A with fine-tuned responses
"""

import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables
knowledge_base = []
model = None

def load_knowledge_base():
    """Load knowledge base from JSONL file"""
    global knowledge_base
    
    try:
        knowledge_base = []

        # Try several candidate paths to locate the dataset in serverless envs
        candidate_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'bee_ai_training_data.jsonl'),
            os.path.join(os.path.dirname(__file__), 'bee_ai_training_data.jsonl'),
            os.path.join(os.getcwd(), 'bee_ai_training_data.jsonl'),
        ]

        jsonl_path = None
        for p in candidate_paths:
            if os.path.exists(p):
                jsonl_path = p
                break

        if jsonl_path:
            logger.info(f"Loading knowledge base from: {jsonl_path}")
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line.strip())
                        knowledge_base.append(entry)
        else:
            # Fallback: create a minimal knowledge base
            logger.warning("JSONL file not found in any known path, using minimal knowledge base")
            knowledge_base = [
                {
                    "messages": [
                        {"role": "user", "content": "When does wild garlic bloom in Germany?"},
                        {"role": "assistant", "content": "Wild garlic typically blooms from late March to early May in central Germany."}
                    ]
                }
            ]
        
        logger.info(f"Loaded {len(knowledge_base)} knowledge entries")
        return True
        
    except Exception as e:
        logger.error(f"Error loading knowledge base: {str(e)}")
        return False

def initialize_gemini():
    """Initialize Gemini API"""
    global model
    
    try:
        # Get API key from environment variable (Vercel)
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable not set")
            return False
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Initialize model (use commonly available model for serverless)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
    
    # Return top 5 most relevant entries
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

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load knowledge base and initialize Gemini
if not load_knowledge_base():
    logger.error("Failed to load knowledge base")
if not initialize_gemini():
    logger.error("Failed to initialize Gemini API")

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
        'gemini_loaded': model is not None,
        'knowledge_base_loaded': len(knowledge_base) > 0,
        'knowledge_entries': len(knowledge_base),
        'env_present': bool(os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')),
        'status': 'healthy'
    })

@app.route('/api/debug-env', methods=['GET'])
def debug_env():
    """Non-secret env status for troubleshooting"""
    key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    masked = None
    if key:
        masked = key[:4] + "***" + key[-4:]
    return jsonify({
        'env_present': bool(key),
        'env_masked': masked,
        'model_initialized': model is not None
    })

# Vercel serverless function handler
def handler(request):
    """Vercel serverless function entry point"""
    return app(request.environ, lambda *args: None)

# For local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
