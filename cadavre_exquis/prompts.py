from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

GEN_SYS="""\
You are a creative, imaginitive writer. You are writing a wiki article related to the following setting:
{setting}

The user will provide a list of reference as well as a partially-complete article.
Your job is to complete the given article, without contradicting any information in the reference.
The reference articles are partially incomplete - do not copy their format, only avoid contradicting their content.
"""
GEN_USR="""\
```
REFERENCE:
{reference}

```
ARTICLE:
{article}"""
GEN_PROMPT=ChatPromptTemplate.from_messages(messages=[
    SystemMessagePromptTemplate.from_template(template=GEN_SYS, input_variables=["setting"]),
    HumanMessagePromptTemplate.from_template(template=GEN_USR, input_variables=["reference", "article"])
]
)


