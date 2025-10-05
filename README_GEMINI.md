# Bee AI - Plant Species Analysis System with Gemini AI

This application combines NASA satellite data analysis with Google Gemini AI-powered chat system specifically trained on bee-related questions and plant phenology data.

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

## Quick Start

### Option 1: Automated Setup (Windows)
1. Get your Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Edit `config.py` file and add your API key: `GEMINI_API_KEY=your_api_key_here`
3. Double-click `start_gemini_ai.bat`
4. Open `index.html` in your browser
5. The AI chat will be available in the left sidebar

### Option 2: Manual Setup

1. **Get Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Edit `config.py` file and add: `GEMINI_API_KEY=your_api_key_here`

2. **Install Python Dependencies**:
   ```bash
   pip install -r requirements_gemini.txt
   ```

3. **Start the Server**:
   ```bash
   python bee_ai_gemini_server.py
   ```

4. **Open the Application**:
   - Open `index.html` in your web browser
   - The AI chat will be available in the left sidebar

## Usage

### Using the AI Chat
1. Click on the "Bee AI" section in the left sidebar
2. Type your question about bees, plants, or honey production
3. Press Enter or click the send button
4. The AI will provide detailed, data-driven answers

### Example Questions
- "When should I place my hives near wild garlic fields in Germany?"
- "What's the best period for honey collection in southern Spain?"
- "How will climate change affect clover blooming in Sweden this year?"
- "When is the right time to expand bee colonies in western Turkey?"

### Using the Map and Dashboard
1. Use the search bar to find specific plant species
2. Apply filters to focus on allergy risks, honey production, or climate impacts
3. Click "Select Beehive Location" to analyze honey production potential
4. Switch between timeline, trends, pollinators, and harvesting tabs

## Technical Details

### AI Model
- **Base Model**: Google Gemini Pro
- **Training Data**: 97 bee-related Q&A pairs covering European plant phenology
- **Knowledge Base**: JSONL format with structured Q&A data
- **API**: RESTful API served via Flask

### Data Sources
- **NASA Satellite Data**: Landsat and MODIS imagery
- **GBIF**: Global Biodiversity Information Facility
- **BloomWatch**: Phenology monitoring and forecasting
- **Plant Database**: Comprehensive species characteristics

### Architecture
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python Flask server
- **AI**: Google Gemini API with custom knowledge base
- **Maps**: Leaflet.js with custom styling
- **Charts**: Chart.js for data visualization

## File Structure

```
nasappsonhal/
├── index.html                    # Main application interface
├── script.js                     # Frontend JavaScript logic
├── styles.css                    # Application styling
├── data.js                       # Plant species database
├── bee_ai_gemini_server.py       # Python Flask server with Gemini API
├── bee_ai_gemini.js              # Frontend Gemini AI integration
├── bee_ai_training_data.jsonl    # Knowledge base (97 Q&A pairs)
├── convert_to_jsonl.py           # Converts training data to JSONL
├── requirements_gemini.txt       # Python dependencies
├── start_gemini_ai.bat           # Windows startup script
└── README.md                     # This file
```

## API Endpoints

- `GET /` - Serves the main HTML file
- `POST /api/chat` - Chat with the Gemini AI
- `GET /api/health` - Server health check
- `GET /api/knowledge` - Knowledge base statistics

## Troubleshooting

### Common Issues

1. **"AI service not responding"**:
   - Make sure the Python server is running (`python bee_ai_gemini_server.py`)
   - Check that port 5000 is not blocked by firewall
   - Verify GEMINI_API_KEY environment variable is set

2. **"Gemini API not available"**:
   - Check your API key is valid
   - Ensure you have internet connection
   - The system will automatically fall back to offline knowledge base

3. **Map not loading**:
   - Check your internet connection
   - Ensure JavaScript is enabled in your browser

### System Requirements

- **Python**: 3.7 or higher
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 100MB free space
- **Browser**: Modern browser with JavaScript enabled
- **Internet**: Required for Gemini API and map tiles
- **API Key**: Google Gemini API key (free tier available)

## Contributing

To add new training data or improve the AI responses:

1. Edit the `training_set` array in `convert_to_jsonl.py`
2. Add new Q&A pairs following the existing format
3. Run: `python convert_to_jsonl.py`
4. Restart the server: `python bee_ai_gemini_server.py`

## License

This project is for educational and research purposes. Please respect the data usage policies of NASA, GBIF, BloomWatch, and Google when using this application.

## API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Edit `config.py` file and add: `GEMINI_API_KEY=your_api_key_here`

The API key is stored securely in `config.py` and is automatically ignored by git for security.
