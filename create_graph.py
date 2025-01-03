from langchain_core.runnables import (RunnableBranch, RunnableLambda, RunnableParallel,RunnablePassthrough)
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts.prompt import PromptTemplate
from pydantic import BaseModel, Field

from typing import Tuple, List, Optional
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
import os
from langchain_community.graphs import Neo4jGraph

from langchain.text_splitter import TokenTextSplitter
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import TextLoader

# from langchain_ollama import ChatOllama
from langchain.chat_models import ChatOllama

from langchain_experimental.graph_transformers import LLMGraphTransformer
from neo4j import GraphDatabase
from langchain_community.vectorstores import Neo4jVector
from langchain_community.vectorstores.neo4j_vector import remove_lucene_chars
from langchain_core.runnables import ConfigurableField, RunnableParallel, RunnablePassthrough


class GraphCreater:     
    def __init__(self, user="neo4j", pw="password", port="7687"):
        self.user = user
        self.pw = pw
        self.port = port
        self.url = f"bolt://localhost:{self.port}"
        self.graph = Neo4jGraph(
            url=self.url,
            username=self.user ,
            password=self.pw ,
        )
    
    def load_data(self, data_path = "./data/data.txt"):
        documents = TextLoader(data_path).load()
        # text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
        # documents = text_splitter.split_documents(documents[:3])
        # print(f"\n documents : ")
        # print(documents) 
        return documents

    def text_to_graph(self, documents, model_name = "llama3"):
        # llm = Ollama(model = model_name, request_timeout = 10000)
        llm = ChatOllama(model=model_name, temperature=0)
        
        # transformer = LLMGraphTransformer(
        #     llm=llm, ignore_tool_usage=False
        # )
        transformer = LLMGraphTransformer(llm=llm)
        graph_documents = transformer.convert_to_graph_documents(documents)
        print(f"\n graph_documents : ")
        print(graph_documents)
        self.graph.add_graph_documents(
            graph_documents,
            baseEntityLabel=True,
            include_source=True
        )
    


def main():
    """ 
    Neo4jでGraph RAGを実行
    https://qiita.com/ksonoda/items/98a6607f31d0bbb237ef
    """
    data_path = "./data/data.txt"
    model_name = "llama3"
    
    graph_creater = GraphCreater()
    documents = graph_creater.load_data(data_path)
    graph_creater.text_to_graph(documents, model_name)
    
    
    

if __name__ == "__main__":
    main()
