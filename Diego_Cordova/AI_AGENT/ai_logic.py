from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.schema.runnable import RunnableLambda
import json
from p import detect_physics_engine_tool

llm = OpenAI()


#####
sos_prompt = PromptTemplate(
    input_variables=["sos_message"],
    template="""
        You are an AI agent responsible for responding to SOS messages in a Rover mission.
        Your mission is to assist when a rover is **stuck** and needs help.

        Instructions:
        - If the SOS message mentions words like "stuck", "trapped", "cannot move", "immobilized", select "rescue_mission".
        - Otherwise, select "unknown_issue".

        Return JSON format:
        {{
            "mission_type": "<rescue_mission/unknown_issue>",
            "notes": "<brief explanation>"
        }}

        SOS Message: {sos_message}
    """,
)

sos_decision_chain = RunnableLambda(lambda x: llm.invoke(sos_prompt.format(**x)))


#####
def detect_physics_engine(physics_data):
    detected_engine = detect_physics_engine_tool.run(physics_data)
    return detected_engine.strip()


###
def analyze_sos_message(sos_message):
    ai_response = sos_decision_chain.invoke({"sos_message": sos_message})
    try:
        parsed_response = json.loads(ai_response)
        return json.dumps(parsed_response)
    except json.JSONDecodeError:
        return json.dumps(
            {"mission_type": "unknown_issue", "notes": "Failed to parse AI response."}
        )
