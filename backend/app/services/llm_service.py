try:
    from langchain_core.prompts import PromptTemplate
    from langchain_core.messages import HumanMessage
except ImportError:
    try:
        from langchain.prompts import PromptTemplate
        from langchain.schema import HumanMessage
    except ImportError:
        PromptTemplate = None
        HumanMessage = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    ChatOllama = None

from app.config import get_settings

class LLMService:
    def __init__(self):
        self.settings = get_settings()
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        try:
            if self.settings.llm_provider == "gemini" and self.settings.gemini_api_key:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=self.settings.gemini_api_key,
                    temperature=0.3
                )
            elif self.settings.llm_provider == "openai" and self.settings.openai_api_key:
                self.llm = ChatOpenAI(
                    model_name="gpt-3.5-turbo",
                    openai_api_key=self.settings.openai_api_key,
                    temperature=0.3
                )
            elif self.settings.llm_provider == "ollama":
                self.llm = ChatOllama(
                    base_url=self.settings.ollama_base_url,
                    model=self.settings.ollama_model,
                    temperature=0.3
                )
        except Exception as e:
            print(f"Warning: Could not initialize LLM provider '{self.settings.llm_provider}': {e}")
            self.llm = None

    def _fallback_extractive_answer(self, prompt: str, context: str, conflicts_str: str = "") -> str:
        """Deterministic structural fallback when no LLM API key is configured or offline."""
        import re
        if not context.strip():
            return "The required information was not found in the available documents."
        
        points = []
        for block in context.split("\n\n"):
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if len(lines) >= 2:
                content = " ".join(lines[1:])
                
                # Split sentences cleanly without breaking numbers like 9.0 or 1.1
                sentences = re.split(r'(?<=[a-zA-Z\)])\.\s+(?=[A-Z0-9])', content)
                for s in sentences:
                    s_clean = s.strip()
                    if s_clean.endswith('.'):
                        s_clean = s_clean[:-1]
                    if len(s_clean) > 20 and not s_clean.isupper():
                        points.append(s_clean)
            elif lines and len(lines[0]) > 20:
                points.append(lines[0])
                
        # Deduplicate while preserving order
        unique_points = []
        for p in points:
            if not any(p[:35].lower() in up.lower() for up in unique_points):
                unique_points.append(p)
            if len(unique_points) >= 4:
                break

        if not unique_points:
            return "The required information was not found in the available documents."

        answer = "Direct Summary:\n"
        for p in unique_points:
            answer += f"- {p}.\n"
            
        if conflicts_str.strip():
            answer += f"\nPolicy Notice:\n- {conflicts_str.strip()}\n"
            
        return answer

    def generate(self, prompt: str, context: str, conflicts_str: str = "") -> str:
        if not context.strip():
            return "The required information was not found in the available documents."

        if not self.llm:
            return self._fallback_extractive_answer(prompt, context, conflicts_str)

        template = """You are an official College Helpdesk Chatbot.
Answer the student's question based ONLY on the provided context documents.

RESPONSE RULES:
1. Keep the answer STRUCTURAL, SHORT, and CLEAR.
2. DO NOT write long paragraphs or vague filler words.
3. Use this structure:
   - **Direct Answer:** 1 short sentence directly answering the question.
   - **Key Rules / Details:**
     • Use bullet points for specific numbers, percentages, dates, or criteria.
     • Keep each bullet point to 1-2 lines.
   - **Important Note:** (Only if there are penalties, fees, deadlines, or exceptions).
4. If there is a policy conflict or revision, state the latest active rule clearly.
5. If the required information is not found in the documents, reply with exactly: 'The required information was not found in the available documents.'

Context Documents:
{context}

Conflict Information (if any):
{conflicts_str}

Student Question: {prompt}
Structured Answer:"""
        
        prompt_template = PromptTemplate(
            input_variables=["context", "conflicts_str", "prompt"],
            template=template
        )
        
        final_prompt = prompt_template.format(
            context=context,
            conflicts_str=conflicts_str,
            prompt=prompt
        )
        
        try:
            response = self.llm.invoke([HumanMessage(content=final_prompt)])
            return response.content
        except Exception as e:
            print(f"LLM API invocation failed ({e}), falling back to verified context extraction.")
            return self._fallback_extractive_answer(prompt, context, conflicts_str)
