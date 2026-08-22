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
        """Deterministic fallback when no LLM API key is configured or offline."""
        if not context.strip():
            return "The required information was not found in the available documents."
        
        # Clean up lines from context
        snippets = []
        for block in context.split("\n\n"):
            lines = [l.strip() for l in block.split("\n") if l.strip()]
            if len(lines) >= 2:
                header = lines[0]
                body = " ".join(lines[1:])
                # Truncate if very long
                if len(body) > 300:
                    body = body[:297] + "..."
                snippets.append(f"{body} {header}")
            elif lines:
                snippets.append(lines[0])
                
        answer = "Based on official institutional records:\n\n"
        answer += "\n\n".join([f"• {s}" for s in snippets[:2]])
        
        if conflicts_str.strip():
            answer += f"\n\n[Policy Notice]: {conflicts_str.strip()}"
            
        return answer

    def generate(self, prompt: str, context: str, conflicts_str: str = "") -> str:
        if not context.strip():
            return "The required information was not found in the available documents."

        if not self.llm:
            return self._fallback_extractive_answer(prompt, context, conflicts_str)

        template = """You are a highly knowledgeable College Helpdesk Chatbot.
Answer the user's question based ONLY on the provided context documents.
Use a short descriptive heading when helpful, followed by numbered steps or bullet points. Keep each point concise and concrete; avoid vague wording and unnecessary paragraphs.
If the required information was not found in the available documents, reply with exactly: 'The required information was not found in the available documents.'
Include citation references to the documents in your answer (e.g., [Document Name, Section]).

Context Documents:
{context}

Conflict Information (if any):
{conflicts_str}

Question: {prompt}
Answer:"""
        
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
