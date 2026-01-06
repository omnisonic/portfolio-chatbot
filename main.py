import streamlit as st
from openai import OpenAI
import json

# Define the LLM engines and their corresponding IDs
llm_engines = {
    "xiaomi/mimo-v2-flash:free": "xiaomi/mimo-v2-flash:free",
}

# Initialize the selected LLM engine
selected_llm_engine = "xiaomi/mimo-v2-flash:free"

# Load portfolio data
def load_portfolio_data():
    try:
        with open('scraped_data.json', 'r') as f:
            data = json.load(f)
        return data
    except Exception as e:
        st.error(f"Error loading portfolio data: {e}")
        return []

portfolio_data = load_portfolio_data()

# Create a context string from portfolio data
def create_portfolio_context():
    if not portfolio_data:
        return "No portfolio data available."
    
    context_parts = []
    for item in portfolio_data:
        if item.get('header') and item.get('description'):
            context_parts.append(f"Project: {item['header']}")
            context_parts.append(f"Description: {item['description']}")
            if item.get('image_urls'):
                context_parts.append(f"Images: {', '.join(item['image_urls'])}")
            if item.get('links'):
                context_parts.append(f"Links: {', '.join(item['links'])}")
            context_parts.append("---")
    
    return "\n".join(context_parts)

portfolio_context = create_portfolio_context()

# Create the Streamlit app
st.title("Portfolio Chatbot 🤖")
with st.sidebar:
    st.header("Settings")
    
    # Create the toggle buttons for selecting the LLM engine
    llm_engines_list = list(llm_engines.values())
    selected_llm_engine = st.radio(
        "Select the LLM engine:",
        llm_engines_list
    )

st.write("**Ask me about the portfolio work!**")


if "messages" not in st.session_state:
    # Initialize with a greeting from Rudy
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": "Hi! I'm Rudy, a graphic designer and product branding specialist. Welcome to my portfolio! Feel free to ask me about my work, projects, or capabilities."
        }
    ]

prompt = st.chat_input("Ask a question...", key="chat_input")

# Define avatar images
user_avatar = "images/rudy_avatar_sm.jpg"
assistant_avatar = "images/rudy_avatar_sm.jpg"

# Display chat history with larger avatars
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Use default Streamlit avatar for user
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        # Use custom image for assistant with width=300
        col1, col2 = st.columns([1, 4])
        with col1:
            st.image(assistant_avatar, width=300)
        with col2:
            st.markdown(f"<div style='margin-top: 0;'>{msg['content']}</div>", unsafe_allow_html=True)

if prompt:
    # Add user message to history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # gets API Key from Streamlit secrets
    client = OpenAI(
    base_url=st.secrets.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
    api_key=st.secrets["OPENROUTER_API_KEY"],
    )
    
    response = client.chat.completions.create(
    model=st.secrets.get("MODEL_NAME", selected_llm_engine),
    messages=[
        {
        "role": "system",
        "content": f"""You are a helpful chatbot representing a creative professional's portfolio. 

CONTEXT - Portfolio Data:
{portfolio_context}

INSTRUCTIONS:
1. Use the portfolio context above to answer questions about the work
2. When relevant, mention specific projects and their details
3. If a project has images, you can reference them or suggest viewing them
4. If a project has links, include them in your response
5. Be conversational but knowledgeable about the portfolio
6. If asked about capabilities, refer to the projects in the context
7. When displaying images or links, use markdown format: [text](url) or ![alt](url)""",
        },
    ]+ st.session_state.messages + [{"role": "user", "content": prompt}],
        )
    
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    
    # Display the assistant's response with larger avatar
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image(assistant_avatar, width=300)
    with col2:
        st.markdown(f"<div style='margin-top: 0;'>{msg}</div>", unsafe_allow_html=True)
    
    # Parse and display any images mentioned in the response
    import re
    image_urls = re.findall(r'https?://[^\s\)]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)', msg)
    if image_urls:
        st.write("**Related Images:**")
        for url in image_urls:
            try:
                st.image(url, use_column_width=True)
            except:
                # If direct image display fails, show as a link
                st.markdown(f"[View Image]({url})")
