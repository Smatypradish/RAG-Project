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
        """Deterministic, question-aware fallback: short relevant points only."""
        import re
        if not context.strip():
            return "The required information was not found in the available documents."

        # Keywords from the student's question (ignore common stop words)
        stop_words = {
            "what", "is", "the", "a", "an", "for", "of", "to", "in", "on", "how",
            "are", "was", "were", "do", "does", "did", "can", "i", "my", "me",
            "and", "or", "by", "with", "from", "at", "be", "been", "it", "this",
            "that", "these", "those", "there", "their", "they", "we", "you", "your",
        }
        keywords = {
            w for w in re.findall(r"[a-zA-Z]{3,}", prompt.lower())
            if w not in stop_words
        }

        def relevance(sentence: str) -> int:
            words = set(re.findall(r"[a-zA-Z]{3,}", sentence.lower()))
            return len(keywords & words)

        # Split context into sentences
        sentences = []
        for block in context.split("\n\n"):
            content = " ".join(l.strip() for l in block.split("\n") if l.strip())
            # Drop the "[Doc: ...]" header line if present
            if content.startswith("["):
                content = content.split("]", 1)[-1]
            for s in re.split(r'(?<=[a-zA-Z\)])\.\s+(?=[A-Z0-9])', content):
                s_clean = s.strip().rstrip(".")
                if len(s_clean) > 25 and not s_clean.isupper():
                    sentences.append(s_clean)

        # Keep only sentences related to the question, most relevant first
        scored = sorted(sentences, key=relevance, reverse=True)
        relevant = [s for s in scored if relevance(s) > 0]

        # Short, clear points: deduplicate, cap length, max 3
        points = []
        for s in relevant:
            if len(s) > 160:
                s = s[:157].rsplit(" ", 1)[0] + "..."
            if not any(s[:30].lower() in p.lower() or p[:30].lower() in s.lower() for p in points):
                points.append(s)
            if len(points) >= 3:
                break

        if not points:
            return "The required information was not found in the available documents."

        answer = "Answer:\n"
        for p in points:
            answer += f"- {p}.\n"

        if conflicts_str.strip():
            answer += f"\nNote:\n- {conflicts_str.strip()}\n"

        return answer

    def generate(self, prompt: str, context: str, conflicts_str: str = "") -> str:
        if not context.strip():
            return "The required information was not found in the available documents."

        if not self.llm:
            return self._fallback_extractive_answer(prompt, context, conflicts_str)

        template = """You are an official College Helpdesk Chatbot.
Answer the student's question based ONLY on the provided context documents.

RESPONSE RULES:
1. Answer in at most 3 short bullet points. Each bullet must be under 20 words.
2. Start with one direct sentence answering the question. No introductions, no filler.
3. Only include information that directly answers the student's question — nothing else.
4. If there is a policy conflict or revision, state the latest active rule clearly in one line.
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
