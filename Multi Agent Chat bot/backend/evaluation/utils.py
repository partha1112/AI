from deepeval.models.base_model import DeepEvalBaseLLM
from backend.agents.llm import llm

class CustomJudge(DeepEvalBaseLLM):
    def __init__(self):
        self.model = llm
    
    def load_model(self):
        return self.model
    
    def generate(self, prompt: str) -> str:
        return self.model.invoke(prompt).content
    
    async def a_generate(self, prompt: str) -> str:
        res = await self.model.ainvoke(prompt)
        return res.content
    
    def get_model_name(self):
        return "Custom GPT-4o-mini Judge"

judge = CustomJudge()
