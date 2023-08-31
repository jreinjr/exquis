from dotenv import load_dotenv
load_dotenv()

from langchain.callbacks.base import BaseCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage
from langchain.schema import LLMResult

from typing import Any, Dict, List


class MyCustomHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        self.token_list = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(type(token))
        print(f"My custom handler, token: {token}")
        self.token_list.append(token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # self.token_list.pop()
        print(f"final token list: {''.join(self.token_list)}")




# To enable streaming, we pass in `streaming=True` to the ChatModel constructor
# Additionally, we pass in a list with our custom handler
chat = ChatOpenAI(max_tokens=25, streaming=True, callbacks=[MyCustomHandler()])

res = chat([HumanMessage(content="Tell me a joke")])
print(res)