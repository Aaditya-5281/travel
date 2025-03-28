import streamlit as st
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import os
from dotenv import load_dotenv
import sys
from io import StringIO
import re

# Load environment variables
load_dotenv()

# Get API key from environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class OutputCapture:
    def __init__(self):
        self.captured_output = StringIO()
        self.old_stdout = None
        
    def start_capture(self):
        self.old_stdout = sys.stdout
        sys.stdout = self.captured_output
        
    def end_capture(self):
        if self.old_stdout:
            sys.stdout = self.old_stdout
            
    def get_captured_text(self):
        return self.captured_output.getvalue()
    
    def clear(self):
        self.captured_output = StringIO()

def clean_agent_messages(text):
    # Remove agent call lines like "user_proxy (to chat_manager):"
    cleaned_text = re.sub(r'^\w+_agent \(to chat_manager\):\s*$', '', text, flags=re.MULTILINE)
    cleaned_text = re.sub(r'^user_proxy \(to chat_manager\):\s*$', '', cleaned_text, flags=re.MULTILINE)
    
    # Remove empty lines that might be left after removing agent calls
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    return cleaned_text

def extract_agent_content(text, agent_name):
    """Extract content from a specific agent"""
    pattern = rf"{agent_name} \(to chat_manager\):\s*(.*?)(?=\w+_agent \(to chat_manager\)|user_proxy \(to chat_manager\)|$)"
    matches = re.findall(pattern, text, re.DOTALL)
    if matches:
        return '\n'.join(matches).strip()
    return ""

def create_agents():
    config_list = [
        {
            'model': 'gpt-4',
            'api_key': OPENAI_API_KEY
        }
    ]

    llm_config = {
        "config_list": config_list,
        "seed": 42,
        "temperature": 0.7,
    }

    code_execution_config = {
        "use_docker": False,
        "work_dir": "workspace",
    }

    planner_agent = AssistantAgent(
        name="planner_agent",
        llm_config=llm_config,
        system_message="You are a helpful assistant that can suggest a travel plan for a user based on their request. After providing your suggestions, end with 'PLANNER COMPLETE'"
    )

    local_agent = AssistantAgent(
        name="local_agent",
        llm_config=llm_config,
        system_message="You are a helpful assistant that can suggest authentic and interesting local activities or places to visit. After providing your suggestions, end with 'LOCAL COMPLETE'"
    )

    language_agent = AssistantAgent(
        name="language_agent",
        llm_config=llm_config,
        system_message="You are a helpful assistant that can provide language tips for the destination. After providing your suggestions, end with 'LANGUAGE COMPLETE'"
    )

    travel_summary_agent = AssistantAgent(
        name="travel_summary_agent",
        llm_config=llm_config,
        system_message="You are a helpful assistant that can compile all suggestions into a final travel plan. Format the plan with clear sections using markdown headers (#). After providing the final plan, end with 'FINAL PLAN COMPLETE'"
    )

    user_proxy = UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: "FINAL PLAN COMPLETE" in x.get("content", ""),
        llm_config=llm_config,
        code_execution_config=code_execution_config
    )

    return planner_agent, local_agent, language_agent, travel_summary_agent, user_proxy

def generate_travel_plan(destination, duration):
    if not OPENAI_API_KEY:
        raise ValueError("OpenAI API key not found. Please check your .env file.")
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    status_text.text("Initializing AI travel agents...")
    
    # Create a capture object
    output_capture = OutputCapture()
    
    try:
        # Start capturing stdout
        output_capture.start_capture()
        
        # Create agents
        planner_agent, local_agent, language_agent, travel_summary_agent, user_proxy = create_agents()
        status_text.text("AI travel agents initialized! Starting planning process...")
        progress_bar.progress(10)
        
        agents = [user_proxy, planner_agent, local_agent, language_agent, travel_summary_agent]
        groupchat = GroupChat(agents=agents, messages=[], max_round=12)
        manager = GroupChatManager(groupchat=groupchat, llm_config={"config_list": [{'model': 'gpt-4', 'api_key': OPENAI_API_KEY}]})

        message = f"""Plan a {duration} day trip to {destination}. Follow these steps:
        1. Planner_agent: Suggest overall itinerary and timing
        2. Local_agent: Add local attractions and activities
        3. Language_agent: Provide essential phrases and language tips
        4. Travel_summary_agent: Compile everything into a final plan with clear sections
        """
        
        # Initialize the chat
        progress_bar.progress(20)
        status_text.text("Generating travel itinerary...")
        user_proxy.initiate_chat(
            manager,
            message=message
        )
        
        # End capturing stdout
        output_capture.end_capture()
        progress_bar.progress(90)
        status_text.text("Finalizing your travel plan...")
        
        # Get the captured terminal output
        terminal_text = output_capture.get_captured_text()
        
        # Extract agent-specific content
        planner_content = extract_agent_content(terminal_text, "planner_agent")
        local_content = extract_agent_content(terminal_text, "local_agent")
        language_content = extract_agent_content(terminal_text, "language_agent")
        summary_content = extract_agent_content(terminal_text, "travel_summary_agent")
        
        # Clean the full terminal output for display
        cleaned_terminal_text = clean_agent_messages(terminal_text)
        
        # Complete progress
        progress_bar.progress(100)
        status_text.text("Travel plan completed!")
        
        # Clear progress elements
        progress_bar.empty()
        status_text.empty()
        
        # Create result container
        st.success(f"✅ Your {duration}-day travel plan for {destination} is ready!")
        
        # Create tabs for different sections
        agent_tabs = st.tabs([
            "📋 Final Plan",
            "🗓️ Planner Details", 
            "🏙️ Local Activities", 
            "🗣️ Language Tips",
            "🔄 Process Log"
        ])
        
        # Display final plan first (most important)
        with agent_tabs[0]:
            st.markdown("## 📋 Final Travel Plan")
            if summary_content:
                # Remove the completion marker for display
                display_content = summary_content.replace("FINAL PLAN COMPLETE", "").strip()
                st.markdown(display_content)
                
                # Add download button for the plan
                st.download_button(
                    label="📥 Download Travel Plan",
                    data=display_content,
                    file_name=f"travel_plan_{destination.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )
            else:
                st.info("No final plan was generated. Please try again.")
        
        # Display other agent outputs in respective tabs
        with agent_tabs[1]:
            st.markdown("## 🗓️ Itinerary Planning")
            if planner_content:
                st.markdown(planner_content.replace("PLANNER COMPLETE", "").strip())
            else:
                st.info("No planner content was generated.")
        
        with agent_tabs[2]:
            st.markdown("## 🏙️ Local Attractions & Activities")
            if local_content:
                st.markdown(local_content.replace("LOCAL COMPLETE", "").strip())
            else:
                st.info("No local activities content was generated.")
        
        with agent_tabs[3]:
            st.markdown("## 🗣️ Language Guide")
            if language_content:
                st.markdown(language_content.replace("LANGUAGE COMPLETE", "").strip())
            else:
                st.info("No language tips were generated.")
        
        # Display process log in last tab (for debugging/interested users)
        with agent_tabs[4]:
            st.markdown("## 🔄 AI Planning Process Log")
            with st.expander("View complete planning process log", expanded=False):
                st.text_area("Process Log", value=cleaned_terminal_text, height=400)
        
        return True
        
    except Exception as e:
        # End capturing if there was an error
        output_capture.end_capture()
        st.error(f"An error occurred: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="AI Travel Planner", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Add a header with logo/icon
    st.markdown("""
    <div style='display: flex; align-items: center; margin-bottom: 20px;'>
        <h1 style='margin: 0;'>🌍 AI Travel Planner</h1>
        <div style='margin-left: auto; font-size: 0.8em; color: #888;'>Powered by AutoGen</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add brief description
    st.markdown("""
    Get a personalized travel itinerary created by AI travel experts. 
    Just tell us where you want to go and for how long!
    """)
    
    # Create a card-like container for inputs
    with st.container():
        st.markdown("""
        <div style='padding: 20px 0;'>
            <h3>Where would you like to travel?</h3>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            destination = st.text_input("Destination:", placeholder="e.g., Tokyo, Japan")
        with col2:
            duration = st.number_input("Duration (days):", min_value=1, max_value=30, value=3)
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            generate_button = st.button("🚀 Plan My Trip!", type="primary", use_container_width=True)
    
    # Divider
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Handle plan generation
    if generate_button:
        if not destination:
            st.warning("⚠️ Please enter a destination")
        else:
            st.markdown(f"### Planning your {duration}-day trip to {destination}...")
            generate_travel_plan(destination, duration)

if __name__ == "__main__":
    main()