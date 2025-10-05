# Bee AI - Plant Species Analysis System

A comprehensive web application that combines NASA satellite data analysis with Google Gemini AI-powered chat system for bee-related questions and plant phenology data.

## Features

- **Interactive Map**: Visualize plant species data with NASA satellite information
- **Gemini AI Chat**: Ask questions about bee behavior, plant blooming times, and honey production
- **Phenology Dashboard**: Track flowering timelines and multi-year trends
- **Hive Management**: Analyze optimal beehive placement and honey yield predictions
- **Real-time Data**: Integration with GBIF and BloomWatch data sources

## AI Chat Capabilities

The Bee AI uses Google Gemini API with a fine-tuned knowledge base covering:
- Plant blooming times across Europe
- Climate change impacts on flowering
- Optimal beehive placement strategies
- Honey production timing and yield predictions
- Pollinator synchronization patterns
- Seasonal nectar flow analysis

## Deployment

### Vercel Deployment

This project is configured for Vercel deployment:

1. **Environment Variables**: Set `GEMINI_API_KEY` in Vercel dashboard
2. **API Structure**: Uses Vercel's serverless functions in `/api` directory
3. **Static Files**: HTML, CSS, JS files served as static assets

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set API Key**:
   ```bash
   export GEMINI_API_KEY=your_api_key_here
   ```

3. **Run Server**:
   ```bash
   python api/handler.py
   ```

4. **Open Application**: Navigate to `http://localhost:5000`

## File Structure

```
nasappsonhal/
├── api/
│   └── handler.py              # Vercel serverless function
├── index.html                  # Main application interface
├── script.js                   # Frontend JavaScript logic
├── styles.css                  # Application styling
├── data.js                     # Plant species database
├── bee_ai_gemini.js            # Frontend Gemini AI integration
├── bee_ai_training_data.jsonl  # Knowledge base (97 Q&A pairs)
├── requirements.txt             # Python dependencies
├── vercel.json                 # Vercel configuration
├── .vercelignore               # Vercel ignore file
└── README.md                   # This file
```

## API Endpoints

- `GET /api/health` - Server health check
- `POST /api/chat` - Chat with the Gemini AI

## Usage

### Using the AI Chat
1. Click on the "Bee AI Assistant" section in the left sidebar
2. Type your question about bees, plants, or honey production
3. Press Enter or click the send button
4. The AI will provide detailed, data-driven answers

### Example Questions
- "When should I place my hives near wild garlic fields in Germany?"
- "What's the best period for honey collection in southern Spain?"
- "How will climate change affect clover blooming in Sweden this year?"
- "When is the right time to expand bee colonies in western Turkey?"

## Technical Details

### AI Model
- **Base Model**: Google Gemini 2.0 Flash
- **Training Data**: 97 bee-related Q&A pairs covering European plant phenology
- **Knowledge Base**: JSONL format with structured Q&A data
- **API**: RESTful API served via Flask/Vercel

### Data Sources
- **NASA Satellite Data**: Landsat and MODIS imagery
- **GBIF**: Global Biodiversity Information Facility
- **BloomWatch**: Phenology monitoring and forecasting
- **Plant Database**: Comprehensive species characteristics

### Architecture
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask server (Vercel serverless)
- **AI**: Google Gemini API with custom knowledge base
- **Maps**: Leaflet.js with custom styling
- **Charts**: Chart.js for data visualization

## Contributing

To add new training data or improve the AI responses:

1. Edit the `bee_ai_training_data.jsonl` file
2. Add new Q&A pairs following the existing format
3. Redeploy to Vercel

## License

This project is for educational and research purposes. Please respect the data usage policies of NASA, GBIF, BloomWatch, and Google when using this application.

## API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Set environment variable in Vercel dashboard: `GEMINI_API_KEY=your_api_key_here`

The API key is free to use with generous rate limits for personal and educational projects."# bloombee" 
