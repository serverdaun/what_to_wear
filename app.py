import os
import streamlit as st
import os
import base64
from smolagents import CodeAgent, HfApiModel, FinalAnswerTool
from tools.get_weather import get_weather_forecast
from utils.utils import load_prompt
from dotenv import load_dotenv
from opentelemetry.sdk.trace import TracerProvider
from openinference.instrumentation.smolagents import SmolagentsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace

if "city" not in st.session_state:
    st.session_state.city = ""
if "age" not in st.session_state:
    st.session_state.age = ""
if "sex" not in st.session_state:
    st.session_state.sex = ""

load_dotenv()
hf_token = os.getenv("HF_TOKEN")

# Set up the OpenTelemetry exporter for LangFuse
LANGFUSE_AUTH = base64.b64encode(
    f"{os.environ.get('LANGFUSE_PUBLIC_KEY')}:{os.environ.get('LANGFUSE_SECRET_KEY')}".encode()
).decode()
os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = os.environ.get("LANGFUSE_HOST") + "/api/public/otel"
os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"
 
# Create a TracerProvider for OpenTelemetry
trace_provider = TracerProvider()

# Add a SimpleSpanProcessor with the OTLPSpanExporter to send traces
trace_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))

# Set the global default tracer provider
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# Instrument smolagents with the configured provider
SmolagentsInstrumentor().instrument(tracer_provider=trace_provider)

def get_clothing_reccomendation(city: str, age: str, sex: str) -> str:
    """
    This function returns clothing recommendations based on the weather forecast for a specific city.
    Args:
        city (str): The name of the city for which to get clothing recommendations.
        age (str): The age of the user for whom to get clothing recommendations.
    Returns:
        str: A string containing clothing recommendations based on the weather forecast.
    """

    # Load prompt for user message for agent
    user_input = load_prompt(
        path="prompts/agent_prompt.yaml",
        prompt_name="user_message",
        city=city,
        age=age,
        sex=sex
    )

    # Define LLM model
    llm = HfApiModel(token=hf_token)

    # Define the list of tools to be used by the agent
    tools = [get_weather_forecast, FinalAnswerTool()]

    # Initialize the CodeAgent with the Hugging Face model.
    agent = CodeAgent(
        model=llm,
        tools=tools,
        max_steps=4,
    )

    # Run the agent with the user input.
    response = agent.run(user_input)
    return response

# Streamlit app
st.title("Clothing Recommendation Agent")
st.write(
    "Get personalized clothing recommendations based on the weather forecast for your city."
)
st.session_state.city = st.text_input("Enter your city:", st.session_state.city)
st.session_state.age = st.text_input("Enter your age:", st.session_state.age)
st.session_state.sex = st.selectbox("Select your gender", options=["Male", "Female"], index=["Male", "Female"].index(st.session_state.sex) if st.session_state.sex else 0)

# Create a button to get the recommendation
if st.button("Get Recommendation"):
    if st.session_state.city and st.session_state.age and st.session_state.sex:
        with st.spinner("Fetching outifit suggestions..."):

            result = get_clothing_reccomendation(
                city=st.session_state.city,
                age=st.session_state.age,
                sex=st.session_state.sex
            )
        st.success("Here are your outfit sugegestions:")
        
        # Display the results
        try:
            for idx, outfit in enumerate(result):
                with st.expander(f"🌟 Style #{idx + 1}: {outfit['style']}", expanded=True):
                    st.markdown(f"**👕 Top:** {outfit['top']}")
                    st.markdown(f"**👖 Bottom:** {outfit['bottom']}")
                    st.markdown(f"**👟 Shoes:** {outfit['shoes']}")
                    st.markdown(f"**🧢 Accessories:** {outfit['accessories']}")
        except Exception as e:
            st.write(result)

    else:
        st.error("Please fill in all fields.")

# Reset button to clear the session state
if st.button("Reset"):
    st.session_state.city = ""
    st.session_state.age = ""
    st.session_state.sex = ""
    st.rerun()