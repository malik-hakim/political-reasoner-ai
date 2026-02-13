# Political Reasoner AI

AI-powered political text analysis application that provides in-depth insights, sentiment analysis, and policy recommendations using OpenAI GPT-4.

## ✨ Key Features

- 📊 **Sentiment Analysis** - Detect political sentiment (positive/negative/neutral)
- 🏷️ **Topic Extraction** - Identify main topics and issues
- 👥 **Entity Detection** - Recognize names, parties, and political positions
- 📝 **Narrative Generation** - Automatic insight summaries
- 💡 **Policy Recommendations** - AI-based policy suggestions
- 💬 **AI Chat** - Interactive discussions about political issues

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API Key

### Installation

```bash
# Clone repository
git clone https://github.com/username/political-reasoner-ai.git
cd political-reasoner-ai

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Running the Application

```bash
python run.py
```

Access the application at `http://localhost:5000`

## 📁 Project Structure

```
political-reasoner-ai/
├── app/
│   ├── __init__.py
│   ├── routes.py           # API endpoints
│   ├── reasoner.py         # Core AI logic
│   ├── openai_manager.py   # OpenAI integration
│   ├── prompts.py          # Prompt templates
│   ├── utils.py            # Utility functions
│   └── templates/
│       └── index.html      # Frontend UI
├── run.py
├── .env.example
└── requirements.txt
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | API health status |
| `/analyze` | POST | Basic text analysis |
| `/complete-analysis` | POST | Complete analysis + narrative |
| `/generate-narrative` | POST | Generate narrative from analysis |
| `/policy-recommendations` | POST | Policy recommendations |
| `/chat` | POST | Chat with political AI |

## 📝 Usage Examples

### Basic Analysis
```python
import requests

response = requests.post('http://localhost:5000/analyze', json={
    'text': 'The government is committed to accelerating public service digitalization...'
})

print(response.json())
```

### Complete Analysis
```python
response = requests.post('http://localhost:5000/complete-analysis', json={
    'text': 'Your political text...',
    'policy_context': 'Government digital transformation'
})
```

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **AI**: OpenAI GPT-4
- **Frontend**: HTML, TailwindCSS, JavaScript
- **Error Handling**: Custom user-friendly error messages

## ⚙️ Configuration

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 👤 Author

M Malik Hakim AR - malikhkm030505@gmail.com

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Flask framework
- TailwindCSS for UI

---

⭐ Star this repository if you find it useful!
