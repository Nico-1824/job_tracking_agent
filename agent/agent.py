from google import genai
from tools.gmail_tools import get_message_content, _get_schema
from tools.spreadsheet_tools import get_companies, add_application, update_application, _get_schema_spreadsheet
import json, os, dotenv
from functools import partial

dotenv.load_dotenv()

class Agent:

    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API"))
        self.tools = [_get_schema(), *_get_schema_spreadsheet()]
        self.max_turns = 20
        self.companies = get_companies()
        self.TOOL_REGISTRY = {
            "get_messages": get_message_content,
            "add_application": add_application,
            "update_application": partial(self._update_application, self.companies),
        }

    @staticmethod
    def _update_application(companies: dict, company: str, status: str) -> bool:
        if company not in companies:
            return False

        row = companies.get(company)
        return update_application(row, status)
    
    def chat(self, prompt: str):

        """This is the function to initiate a conversation with the agent and give it its tasks"""


        interaction = self.client.interactions.create(
            model="gemini-3.5-flash",
            system_instruction = (
                "You are an agent that tracks job applications and what state they are in. "
                "You will scan emails and determine which ones are actually about job applications, "
                "as opposed to unrelated emails or general news/announcements from La Salle University "
                "that are not about a specific application -- ignore emails that don't concern a job "
                "application's status.\n\n"
            
                "For each job-application-related email you find, you will cross reference the tracked companies"
                " that will be in the input at the start of the conversation. If it is not being added you will use the add_application tool"
                " to add the application to the spreadsheet for tracking, if it is being tracked you can update the status accordingly with the "
                "update_application tool."
            
                "Only include a recruiter name if the email is a personal message from a specific "
                "named individual, such as one scheduling an interview or reaching out directly -- "
                "never from an automated or no-reply sender. Omit the recruiter field otherwise.\n\n"
            
                "Keep working through every distinct company you find across all the emails you scan -- "
                "call the appropriate tool once per company, and don't stop after just one. Only "
                "respond with a final summary once there is nothing left to add or update."
            ),
            input=prompt + f"Tracked applications are: {self.companies}",
            tools=self.tools
        )

        for turn in range(self.max_turns):

            function_queue = []
            function_results = []
            for step in interaction.steps:

                # check if there is functions to be done, if yes run them, if no, theres nothing else to do 
                # return final response
                if step.type == "function_call":
                    function_queue.append(step)
            
            if not function_queue:
                return interaction.output_text
            else:
                for fn in function_queue:
                    fn_call = self.TOOL_REGISTRY.get(fn.name)
                    print(f"Calling function: {fn_call}")
                    result = fn_call(**fn.arguments)
                    function_results.append({
                        "type": "function_result",
                        "name": fn.name,
                        "call_id": fn.id,
                        "result": [{"type": "text", "text": json.dumps(result)}]
                    })
            
            interaction = self.client.interactions.create(
                model="gemini-3.5-flash",
                input=function_results,
                previous_interaction_id=interaction.id,
                tools=self.tools
            )

        return "Reached max turns, no final result, check for loop"