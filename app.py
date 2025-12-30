import streamlit as st
import openai
import requests

# =============================================
# ENTER YOUR API KEY HERE
# =============================================
OPENAI_API_KEY = "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"  # Replace with your actual OpenAI API key
# =============================================

# Page configuration
st.set_page_config(
    page_title="Real Estate Q&A with AI",
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
st.title("🏠 Real Estate Q&A with AI")
st.markdown("*Powered by OpenAI GPT-4 with weather information for home tours*")

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
if OPENAI_API_KEY == "sk-proj-your-api-key-here":
    st.error("⚠️ Please edit app.py and enter your OpenAI API key in the OPENAI_API_KEY variable at the top of the file.")
    st.info("Get your API key from: https://platform.openai.com/api-keys")
    st.stop()

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

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
    
    # Get AI response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Prepare messages with system prompt
            api_messages = [
                {
                    "role": "system",
                    "content": "You are a knowledgeable real estate expert. Provide helpful, accurate information about real estate topics including buying, selling, investing, market trends, financing, property management, and related subjects. Be conversational and practical in your advice. If users mention weather or touring homes, you can incorporate weather information they may have checked into your advice."
                }
            ] + [
                {"role": msg["role"], "content": msg["content"]}
                for msg in st.session_state.messages
            ]
            
            # Create streaming response
            full_response = ""
            
            stream = openai.chat.completions.create(
                model="gpt-4o",  # Using GPT-4o (faster and cheaper than GPT-4)
                messages=api_messages,
                max_tokens=1024,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
            
        except openai.AuthenticationError as e:
            st.error("❌ Invalid API key. Please check your OpenAI API key in the code.")
            st.error(f"Details: {str(e)}")
            st.info("Your API key should start with 'sk-proj-' and be from platform.openai.com")
        except openai.RateLimitError:
            st.error("⏱️ Rate limit exceeded. Please wait a moment and try again.")
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with Streamlit and OpenAI GPT-4"
    "</div>",
    unsafe_allow_html=True
)
