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
    data = []
    try:
        with open('scraped_data.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"Error loading scraped_data.json: {e}")
    
    try:
        with open('rudy-knowledge-v01.md', 'r') as f:
            knowledge_content = f.read()
        # Parse the markdown file and convert to a format similar to scraped_data
        knowledge_data = parse_knowledge_base(knowledge_content)
        data.extend(knowledge_data)
    except Exception as e:
        st.error(f"Error loading rudy-knowledge-v01.md: {e}")
    
    return data

# Parse the knowledge base markdown file
def parse_knowledge_base(content):
    """Parse the markdown knowledge base and convert to list of knowledge items"""
    knowledge_items = []
    lines = content.split('\n')
    
    current_item = {}
    current_content = []
    
    for line in lines:
        line = line.strip()
        
        # Check for chunk headers
        if line.startswith('<!-- chunk:id='):
            # Save previous item if exists
            if current_item:
                if 'description' not in current_item:
                    current_item['description'] = '\n'.join(current_content).strip()
                knowledge_items.append(current_item)
                current_content = []
            
            # Start new item
            current_item = {'type': 'knowledge'}
            # Extract chunk ID and tags
            chunk_info = line.replace('<!-- chunk:id=', '').replace(' -->', '')
            parts = chunk_info.split('; ')
            if parts:
                current_item['header'] = parts[0].replace('-', ' ').title()
                if len(parts) > 1:
                    tags = parts[1].replace('tags=', '').split(',')
                    current_item['tags'] = tags
        
        # Check for knowledge base title
        elif line.startswith('# Rudy Knowledge Base'):
            continue
            
        # Skip empty lines between chunks
        elif line == '' and not current_content:
            continue
            
        # Add content lines
        elif line and not line.startswith('<!--'):
            current_content.append(line)
    
    # Add the last item
    if current_item and current_content:
        if 'description' not in current_item:
            current_item['description'] = '\n'.join(current_content).strip()
        knowledge_items.append(current_item)
    
    return knowledge_items

portfolio_data = load_portfolio_data()

# Create a context string from portfolio data
def create_portfolio_context():
    if not portfolio_data:
        return "No portfolio data available."
    
    context_parts = []
    
    # Separate projects from knowledge items
    projects = [item for item in portfolio_data if 'image_urls' in item or 'links' in item]
    knowledge = [item for item in portfolio_data if 'type' in item and item['type'] == 'knowledge']
    
    # Add projects section
    if projects:
        context_parts.append("=== PORTFOLIO PROJECTS ===")
        for item in projects:
            if item.get('header') and item.get('description'):
                context_parts.append(f"Project: {item['header']}")
                context_parts.append(f"Description: {item['description']}")
                if item.get('image_urls'):
                    context_parts.append(f"Images: {', '.join(item['image_urls'])}")
                if item.get('links'):
                    context_parts.append(f"Links: {', '.join(item['links'])}")
                context_parts.append("---")
    
    # Add knowledge section
    if knowledge:
        context_parts.append("\n=== RUDY'S KNOWLEDGE & BACKGROUND ===")
        for item in knowledge:
            if item.get('header') and item.get('description'):
                context_parts.append(f"{item['header']}:")
                context_parts.append(item['description'])
                if item.get('tags'):
                    context_parts.append(f"Tags: {', '.join(item['tags'])}")
                context_parts.append("---")
    
    return "\n".join(context_parts)

portfolio_context = create_portfolio_context()

# Create the Streamlit app
st.title("Portfolio Chatbot")

st.write("**Ask me about my portfolio work!**")


if "messages" not in st.session_state:
    # Initialize with a greeting from Rudy
    st.session_state["messages"] = [
        {
            "role": "assistant", 
            "content": "Hi! I'm Rudy, a graphic designer and product branding specialist. Welcome to my portfolio! Feel free to ask me about my work, projects, or capabilities."
        }
    ]

# Your existing chat input
prompt = st.chat_input("Ask a question...", key="chat_input")


# Define avatar images
user_avatar = "images/rudy_avatar_sm.jpg"
assistant_avatar = "images/rudy_avatar_sm.jpg"

# Add responsive CSS for mobile devices
st.markdown("""
<style>
    /* Assistant avatar wrapper - containers around st.image() */
    .assistant-avatar-wrapper {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }
    
    /* Target st.image() containers for assistant avatars */
    .assistant-avatar-wrapper div[data-testid="stVerticalBlock"] {
        width: 80px !important;
        height: 80px !important;
        overflow: hidden !important;
        border-radius: 50% !important;
    }
    
    .assistant-avatar-wrapper img {
        width: 80px !important;
        height: 80px !important;
        object-fit: cover !important;
        border-radius: 50% !important;
    }
    
    /* Mobile responsive avatar sizing */
    @media (max-width: 768px) {
        .assistant-avatar-wrapper div[data-testid="stVerticalBlock"] {
            width: 50px !important;
            height: 50px !important;
        }
        
        .assistant-avatar-wrapper img {
            width: 50px !important;
            height: 50px !important;
        }
        
        .assistant-message-container {
            margin-top: 0 !important;
            font-size: 14px !important;
            line-height: 1.4 !important;
        }
    }
    
    /* Desktop avatar sizing */
    @media (min-width: 769px) {
        .assistant-message-container {
            margin-top: 0 !important;
        }
    }
    
    /* Ensure proper spacing */
    .stMarkdown {
        margin: 0 !important;
    }
    
    /* Ensure content images remain rectangular */
    .assistant-message-container img {
        border-radius: 8px !important;
        max-width: 100% !important;
        height: auto !important;
        width: auto !important;
    }
    
    /* Make sure related images section images stay rectangular */
    div[data-testid="stVerticalBlock"] img:not(.assistant-avatar-wrapper img) {
        border-radius: 8px !important;
        max-width: 100% !important;
        height: auto !important;
        width: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Display chat history with responsive avatars
for msg in st.session_state.messages:
    if msg["role"] == "user":
        # Use default Streamlit avatar for user
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        # Use responsive layout for assistant
        col1, col2 = st.columns([0.15, 0.85])
        with col1:
            # Use st.image with container for proper sizing
            st.markdown('<div class="assistant-avatar-wrapper">', unsafe_allow_html=True)
            st.image(assistant_avatar, width=80)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="assistant-message-container">{msg["content"]}</div>', unsafe_allow_html=True)

# Show suggested questions only after the greeting message
if len(st.session_state.messages) == 1 and st.session_state.messages[0]["role"] == "assistant":
    st.write("**You can ask things like:**")
    suggested_questions = [
    
        "Can you show me your branding work?",
        "What's your design process like?",
            "Can you tell me a joke?",
    ]
    
    # Display buttons vertically
    for i, question in enumerate(suggested_questions):
        if st.button(question, key=f"suggest_{i}"):
            # Directly process the question without modifying session state
            # Add user message to history
            st.session_state.messages.append({"role": "user", "content": question})
            
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
                "content": f"""You are a graphic designer and product branding specialist. 

CONTEXT - Portfolio Data:
{portfolio_context}

INSTRUCTIONS:
1. Use the portfolio context above to answer questions about the work
2. When relevant, mention ONE specific project and its details only
3. Keep your response focused on a single example
4. If the project has images, include ONE image in your response
5. If the project has links, include them in your response
6. Be conversational but knowledgeable about the portfolio
7. Always end your response by asking: "Would you like to see another example?"
8. When displaying images or links, use markdown format: [text](url) or ![alt](url)""",
                },
            ]+ st.session_state.messages + [{"role": "user", "content": question}],
            max_tokens=500,
                )
            
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun()

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
        "content": f"""You are a graphic designer and product branding specialist. 

CONTEXT - Portfolio Data:
{portfolio_context}

INSTRUCTIONS:
1. Use the portfolio context above to answer questions about the work
2. When relevant, mention ONE specific project and its details only
3. Keep your response focused on a single example
4. If the project has images, include ONE image in your response
5. If the project has links, include them in your response
6. Be conversational but knowledgeable about the portfolio
7. Always end your response by asking: "Would you like to see another example?"
8. When displaying images or links, use markdown format: [text](url) or ![alt](url)""",
        },
    ]+ st.session_state.messages + [{"role": "user", "content": prompt}],
    max_tokens=500,
        )
    
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    
    # Display the assistant's response with responsive avatar
    col1, col2 = st.columns([0.15, 0.85])
    with col1:
        st.markdown('<div class="assistant-avatar-wrapper">', unsafe_allow_html=True)
        st.image(assistant_avatar, width=80)
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="assistant-message-container">{msg}</div>', unsafe_allow_html=True)
    
    # Parse and display any images mentioned in the response
    import re
    image_urls = re.findall(r'https?://[^\s\)]+(?:\.jpg|\.jpeg|\.png|\.gif|\.webp)', msg)
    if image_urls:
        st.write("**Related Images:**")
        for url in image_urls:
            try:
                st.image(url, width=400)
            except:
                # If direct image display fails, show as a link
                st.markdown(f"[View Image]({url})")
