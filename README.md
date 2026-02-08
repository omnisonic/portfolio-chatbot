# Portfolio Chatbot - Standalone Streamlit App


A standalone Streamlit chatbot that answers questions about a creative professional's portfolio using OpenAI API via OpenRouter.

![Portfolio Screenshot](images/screen%20shot%20portfolio-chatbot.JPG)

## Features

- Chat interface with portfolio-specific Q&A
- Custom assistant avatar display
- Multiple LLM engine selection
- Portfolio context integration
- Image display support in responses

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Secrets

Create a `.streamlit/secrets.toml` file or configure these secrets in Streamlit Cloud:

```toml
OPENROUTER_API_KEY = "your-openrouter-api-key-here"
# Optional:
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "xiaomi/mimo-v2-flash:free"
```

### 3. Run Locally

```bash
streamlit run main.py
```

## Deployment to Streamlit Cloud

1. **Push to GitHub**: Upload this entire folder to a GitHub repository
2. **Connect to Streamlit Cloud**: 
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub account
   - Select your repository and this folder
3. **Configure Secrets**: Add the required secrets in the Streamlit Cloud dashboard
4. **Deploy**: Click "Deploy" and wait for the app to build

## File Structure

```
portfolio-chatbot/
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── scraped_data.json       # Portfolio data
├── images/
│   └── rudy_avatar_sm.jpg  # Assistant avatar
└── README.md              # This file
```

## Required Secrets

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `OPENROUTER_BASE_URL` (optional): API base URL (defaults to OpenRouter)
- `MODEL_NAME` (optional): Model selection (defaults to xiaomi/mimo-v2-flash:free)

## Usage

1. Start a conversation by typing in the chat input
2. Ask questions about the portfolio work
3. The bot will respond using the portfolio context
4. Images mentioned in responses will be displayed automatically

## Notes

- The app uses Streamlit's built-in chat interface for user messages
- Assistant messages display with a custom avatar (300px width)
- Portfolio data is loaded from `scraped_data.json`
- The app supports multiple LLM engines via the sidebar selection
