from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.callbacks.base import AsyncCallbackHandler, BaseCallbackHandler
from langchain.schema import LLMResult, HumanMessage
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma

from typing import Any, Dict, List
import asyncio
import langchain
import spacy

from cadavre_exquis.prompts import *

class CustomSyncHandler(BaseCallbackHandler):

    def __init__(self, article_ref: List[str], article_index) -> None:
        super().__init__()
        self.article_ref = article_ref
        self.article_index = article_index
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        self.token_list = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.token_list.append(token)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        if self.token_list[-1] == '':
            self.token_list.pop()
        if self.token_list[0] == '':
            self.token_list[0] = ' '

        print(f"appending {self.token_list} to {self.article_ref[self.article_index]}")
        self.article_ref[self.article_index] += "".join(self.token_list)
        print(f"new string: {self.article_ref[self.article_index]}")
        current_article = nlp(self.article_ref[self.article_index])
        sentences = list(current_article.sents)
        if len(sentences) > 1:
            print('\n\n\n!!!!SENTENCE DETECTED!!!!\n' + str(sentences[-2])+"\n\n\n")
        

NUM_ARTICLES = 5
MAX_TOKENS = 10
MAX_ITERS = 100

SETTING = "Neo-Kowloon, a cyberpunk enclave reminiscent of the infamous walled city"
TOPIC_0 = "# FASHION TRENDS\n"
TOPIC_1 = "# HISTORY\n"
TOPIC_2 = "# TECHNOLOGY\n"
TOPIC_3 = "# CULTURE\n"
TOPIC_4 = "# LAW ENFORCEMENT & CRIME\n"




# langchain.debug = True

def get_llm_chain_with_callbacks(article_ref, index) -> LLMChain:
    llm = ChatOpenAI(model='gpt-4', temperature=0.8, max_tokens=MAX_TOKENS, streaming=True, callbacks=[CustomSyncHandler(article_ref, index)])
    return LLMChain(llm=llm, prompt=GEN_PROMPT)

def get_article_and_reference(article_ref:List[str], index:int) -> (str, str):
    duplicate_list = article_ref[:]
    article = duplicate_list.pop(index)
    # single_ref = article_ref[(index + 1) % len(article_ref)]
    ref_string = "\n\n".join((duplicate_list))
    #ref_string = "\n" + single_ref + "\n"
    return article, ref_string

async def process_article(i):
    article, ref_string = get_article_and_reference(article_ref=article_ref, index=i)
    print(f'article:\n{article}\nref_string:\n{ref_string}')
    res = await llms[i].apredict(setting=SETTING, reference=ref_string, article=article, llm_kwargs={"frequency_penalty":1, "logit_bias":{2: -100, 1303:-100, 2235:-100, 22492:-100}})
    print("OUTPUT:\n\n"+res + "\n\n")

# article_ref = [""] * NUM_ARTICLES
# topics = [TOPIC_0, TOPIC_1, TOPIC_2, TOPIC_3, TOPIC_4]
article_ref = [TOPIC_0, TOPIC_1, TOPIC_2, TOPIC_3, TOPIC_4]
llms = [get_llm_chain_with_callbacks(article_ref=article_ref, index=i) for i in range(len(article_ref))]
nlp = spacy.load("en_core_web_md")

async def main():
    for _ in range(MAX_ITERS):
        tasks = [process_article(i) for i in range(len(article_ref))]
        await asyncio.gather(*tasks)

    print("\n\nFINAL OUTPUT:\n"+ "\n".join(article_ref))

asyncio.run(main())