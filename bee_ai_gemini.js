// Bee AI - Gemini API Integration (Frontend)
// This provides AI responses using Google Gemini API with fine-tuned knowledge base

class BeeAIGemini {
    constructor() {
        // Compute base API URL for local (localhost) vs deployed (relative)
        const isLocal = typeof window !== 'undefined' && window.location && 
                       (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
        this.baseUrl = isLocal ? 'http://localhost:5001' : ''; // Empty for Vercel (relative paths)
        this.isOnline = false;
        this.knowledgeBase = this.initializeFallbackKnowledge();

        // Warm-up/keep-alive ping to reduce serverless cold starts while page is open
        try {
            this.pingHealth();
            setInterval(() => this.pingHealth(), 5 * 60 * 1000); // every 5 minutes
        } catch (_) {}
    }

    initializeFallbackKnowledge() {
        // Fallback knowledge base for when API is not available
        return {
            "germany": {
                "wild garlic": "Wild garlic typically blooms from late March to early May in central Germany. Move hives in early April for peak nectar flow.",
                "clover": "Clover blooms from late May to early July in Bavaria. Peak nectar flow is expected in mid-June.",
                "honesty": "Honesty blooms from late March to mid-May in most parts of Germany.",
                "sunflower": "Sunflowers dominate summer bloom from July through August in eastern Germany."
            },
            "spain": {
                "sunflower": "Sunflowers in southern Spain reach full bloom between late June and August. Start honey collection in mid-July.",
                "clover": "Early clover typically starts blooming in late April in central Spain, signaling the beginning of nectar flow.",
                "lavender": "Lavender blooms in June and July in central Spain. Peak nectar occurs in late June."
            },
            "turkey": {
                "honesty": "Honesty flowers appear from mid-March through April in western Turkey. Late March is the best expansion period.",
                "wild garlic": "Wild garlic typically blooms from March to April in northwestern Turkey. Nectar flow starts around the last week of March.",
                "sunflower": "Sunflowers bloom July–August across central Turkey. Start honey collection by mid-July for the best yield."
            },
            "sweden": {
                "clover": "Clover blooms from May through July in Sweden, with peak nectar in June.",
                "honesty": "Honesty and wild garlic are key early bloomers, flowering from mid-April to May.",
                "heather": "Heather provides nectar from August to September in southern Sweden."
            },
            "general": {
                "hive placement": "Place hives near early blooming flowers like wild garlic and honesty for spring buildup.",
                "honey collection": "Start honey collection when flowers reach full bloom, typically mid-season.",
                "climate change": "Warmer springs may advance flowering by 7-10 days, requiring earlier hive placement.",
                "drought": "Drought conditions may shorten bloom periods by up to two weeks, plan for earlier harvests."
            }
        };
    }

    async generateResponse(question) {
        // Try Gemini API first
        try {
            const apiUrl = `${this.baseUrl}/api/chat`;

            const response = await this.fetchWithTimeout(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            }, 12000);
            
            if (response.ok) {
                const data = await response.json();
                this.isOnline = true;
                return data.answer;
            } else {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
        } catch (error) {
            // One quick retry in case of cold start
            try {
                const apiUrl = `${this.baseUrl}/api/chat`;
                const response = await this.fetchWithTimeout(apiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                }, 12000);
                if (response.ok) {
                    const data = await response.json();
                    this.isOnline = true;
                    return data.answer;
                }
            } catch (_) {}

            console.log('Gemini API not available, using fallback knowledge...');
            this.isOnline = false;
            return this.generateFallbackResponse(question);
        }
    }

    async fetchWithTimeout(url, options, timeoutMs = 10000) {
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeoutMs);
        try {
            const res = await fetch(url, { ...options, signal: controller.signal });
            return res;
        } finally {
            clearTimeout(id);
        }
    }

    generateFallbackResponse(question) {
        const lowerQuestion = question.toLowerCase();
        const countries = Object.keys(this.knowledgeBase);
        
        // Find country context
        let country = null;
        for (const c of countries) {
            if (lowerQuestion.includes(c)) {
                country = c;
                break;
            }
        }

        // Find plant context
        const plants = ["wild garlic", "clover", "honesty", "sunflower", "lavender", "heather", "acacia", "linden", "chestnut"];
        let plant = null;
        for (const p of plants) {
            if (lowerQuestion.includes(p)) {
                plant = p;
                break;
            }
        }

        // Find topic context
        const topics = ["hive placement", "honey collection", "climate change", "drought"];
        let topic = null;
        for (const t of topics) {
            if (lowerQuestion.includes(t)) {
                topic = t;
                break;
            }
        }

        // Generate response
        let response = "";
        
        if (country && plant && this.knowledgeBase[country][plant]) {
            response = this.knowledgeBase[country][plant];
        } else if (topic && this.knowledgeBase.general[topic]) {
            response = this.knowledgeBase.general[topic];
        } else {
            response = this.generateGenericResponse(question);
        }

        // Keep responses concise and neutral when offline
        return response;
    }

    generateGenericResponse(question) {
        const responses = [
            "For optimal bee health and honey production, timing is crucial. Monitor local flowering patterns and adjust hive placement accordingly.",
            "Bee colonies thrive when placed near diverse flowering sources. Consider seasonal bloom patterns for maximum nectar availability.",
            "Climate conditions significantly affect flowering times. Warmer springs typically advance bloom periods by 7-10 days.",
            "Successful beekeeping requires understanding local plant phenology. Track flowering calendars for your specific region.",
            "Honey production peaks when flowers reach full bloom. Plan hive placement to coincide with peak nectar flow periods.",
            "Drought conditions can shorten flowering periods. Monitor weather patterns and adjust harvest timing accordingly.",
            "Early spring flowers like wild garlic and honesty provide crucial early-season nectar for colony buildup.",
            "Summer flowers like sunflowers offer abundant nectar but require careful timing for optimal honey collection."
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    async checkApiStatus() {
        try {
            const apiUrl = `${this.baseUrl}/api/health`;
            
            const response = await fetch(apiUrl);
            if (response.ok) {
                const data = await response.json();
                return data;
            }
        } catch (error) {
            console.log('API status check failed:', error);
        }
        return null;
    }

    async pingHealth() {
        try {
            await fetch(`${this.baseUrl}/api/health`, { method: 'GET' });
        } catch (_) {}
    }
}

// Initialize Bee AI Gemini
const beeAI = new BeeAIGemini();

// Override the sendAIMessage function to use Gemini API
async function sendAIMessage() {
    const chatInput = document.getElementById('chatInput');
    const chatMessages = document.getElementById('chatMessages');
    const question = chatInput.value.trim();
    
    if (!question) return;
    
    // Add user message to chat
    addMessageToChat(question, 'user');
    chatInput.value = '';
    
    // Show loading indicator
    const loadingId = addMessageToChat('Thinking...', 'ai', true);
    
    try {
        // Use Gemini AI
        const response = await beeAI.generateResponse(question);
        
        // Remove loading message
        removeMessageFromChat(loadingId);
        
        // Add AI response
        addMessageToChat(response, 'ai');
        
        // Show API status
        if (beeAI.isOnline) {
            console.log('✅ Using Gemini API');
        } else {
            console.log('⚠️ Using fallback knowledge base');
        }
        
    } catch (error) {
        console.error('Error generating AI response:', error);
        
        // Remove loading message
        removeMessageFromChat(loadingId);
        
        // Add error message
        addMessageToChat('I apologize, but I encountered an error processing your question. Please try again.', 'ai');
    }
}
