# 🌍 AI Travel Planner

A powerful AI-powered travel planning application that creates personalized travel itineraries using multiple AI agents. Built with Streamlit and AutoGen, this application provides comprehensive travel plans including itinerary suggestions, local activities, and language tips.

## ✨ Features

- **Multi-Agent Planning System**: Utilizes specialized AI agents for different aspects of travel planning:
  - Planner Agent: Creates overall itinerary and timing
  - Local Agent: Suggests authentic local attractions and activities
  - Language Agent: Provides essential phrases and language tips
  - Travel Summary Agent: Compiles everything into a final comprehensive plan

- **Interactive UI**: Clean and intuitive Streamlit interface
- **Progress Tracking**: Real-time progress updates during plan generation
- **Organized Output**: Tabbed interface showing different aspects of the travel plan
- **Downloadable Plans**: Export your travel plan as a markdown file
- **Detailed Process Log**: Access to the complete AI planning process for transparency

## 🚀 Getting Started

### Prerequisites

- Python 3.7+
- OpenAI API key
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd travel
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

### Running the Application

1. Start the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## 💡 Usage

1. Enter your desired destination in the text input field
2. Select the duration of your trip (1-30 days)
3. Click "Plan My Trip!" to generate your travel plan
4. View the generated plan in the organized tabs:
   - Final Plan: Complete travel itinerary
   - Planner Details: Detailed day-by-day planning
   - Local Activities: Local attractions and activities
   - Language Tips: Essential phrases and language guidance
   - Process Log: Complete AI planning process

## 🛠️ Technical Details

- Built with Streamlit for the frontend
- Uses AutoGen for AI agent orchestration
- Implements OpenAI's GPT-4 model for intelligent planning
- Features a modular architecture with specialized AI agents

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This application requires an OpenAI API key and may incur costs based on API usage. Please review OpenAI's pricing and terms of service before using this application. 
