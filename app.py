import streamlit as st
import anthropic
import requests

# =============================================
# ENTER YOUR API KEY HERE
# =============================================
CLAUDE_API_KEY = "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"  # Replace with your actual API key
# =============================================

# Page configuration
st.set_page_config(
    page_title="Real Estate Q&A with Claude",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to bottom right, #EFF6FF, #E0E7FF);
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("🏠 Real Estate Q&A with Claude")
st.markdown("*Powered by Claude AI with weather information for home tours*")

# Sidebar for weather and settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Weather section
    st.header("🌤️ Weather for Home Tours")
    
    city = st.text_input(
        "City Name",
        placeholder="e.g., New York, London, Tokyo",
        help="Enter city name to check weather"
    )
    
    if st.button("Check Weather", type="primary"):
        if city:
            try:
                # Using wttr.in API (completely free, no key required)
                weather_url = f"https://wttr.in/{city}?format=j1"
                response = requests.get(weather_url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    current = data['current_condition'][0]
                    
                    st.success(f"**Weather in {city}**")
                    st.metric("Temperature", f"{current['temp_F']}°F ({current['temp_C']}°C)")
                    st.metric("Condition", current['weatherDesc'][0]['value'])
                    st.metric("Humidity", f"{current['humidity']}%")
                    st.metric("Wind Speed", f"{current['windspeedMiles']} mph")
                    
                    # 3-day forecast
                    st.markdown("**3-Day Forecast:**")
                    for day in data['weather'][:3]:
                        date = day['date']
                        max_temp = day['maxtempF']
                        min_temp = day['mintempF']
                        desc = day['hourly'][0]['weatherDesc'][0]['value']
                        st.write(f"📅 {date}: {min_temp}°F - {max_temp}°F, {desc}")
                else:
                    st.error("Could not fetch weather data. Please check the city name.")
            except Exception as e:
                st.error(f"Error fetching weather: {str(e)}")
        else:
            st.warning("Please enter a city name")
    
    st.divider()
    
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Example Questions:**")
    st.markdown("""
    - What should first-time buyers know?
    - How does mortgage pre-approval work?
    - What are closing costs?
    - Is now a good time to buy?
    - What's the best weather for touring homes?
    """)

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Check if API key is set
if CLAUDE_API_KEY == "sk-ant-your-api-key-here":
    st.error("⚠️ Please edit app.py and enter your Claude API key in the CLAUDE_API_KEY variable at the top of the file.")
    st.info("Get your API key from: https://console.anthropic.com/")
    st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about real estate..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get Claude's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Initialize Anthropic client
            client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
            
            # Prepare messages for API
            api_messages = [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages
            ]
            
            # Create message with streaming
            full_response = ""
            
            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system="You are a knowledgeable real estate expert. Provide helpful, accurate information about real estate topics including buying, selling, investing, market trends, financing, property management, and related subjects. Be conversational and practical in your advice. If users mention weather or touring homes, you can incorporate weather information they may have checked into your advice.",
                messages=api_messages
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
            
        except anthropic.AuthenticationError:
            st.error("❌ Invalid API key. Please check your Claude API key in the code.")
        except anthropic.RateLimitError:
            st.error("⏱️ Rate limit exceeded. Please wait a moment and try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with Streamlit and Claude AI"
    "</div>",
    unsafe_allow_html=True
)
