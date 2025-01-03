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

from langchain_ollama import OllamaEmbeddings
from langchain_experimental.llms.ollama_functions import OllamaFunctions


class GraphRAG:
    def __init__(self, model_name = "llama3", user="neo4j", pw="password", port="7687"):
        self.user = user
        self.pw = pw
        self.port = port
        self.url = f"bolt://localhost:{self.port}"
        self.graph = Neo4jGraph(
            url=self.url,
            username=self.user ,
            password=self.pw ,
        )
        self.model_name = model_name
        self.entity_chain = None
        self.vector_retriever = None
        
    def generate_full_text_query(self, input: str) -> str:
        """
        指定された入力文字列に対する全文検索クエリを生成します。

        この関数は、全文検索に適したクエリ文字列を構築します。
        入力文字列を単語に分割し、
        各単語に対する類似性のしきい値 (変更された最大 2 文字) を結合します。
        AND 演算子を使用してそれらを演算します。ユーザーの質問からエンティティをマッピングするのに役立ちます
        データベースの値と一致しており、多少のスペルミスは許容されます。
        """
        full_text_query = ""
        words = [el for el in remove_lucene_chars(input).split() if el]
        for word in words[:-1]:
            full_text_query += f" {word}~2 AND"
        full_text_query += f" {words[-1]}~2"
        return full_text_query.strip()
    
    
    def structured_retriever(self, question: str) -> str:
        """
        質問の中で言及されたエンティティの近傍を収集します。
        """
        result = ""
        entities = self.entity_chain.invoke({"question": question})
        self.graph.query("CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]")
        print(f"\n-------entities: \n{entities}")
        for entity in entities.names:
            response = self.graph.query(
                """CALL db.index.fulltext.queryNodes('entity', $query)
                YIELD node,score
                CALL {
                WITH node
                MATCH (node)-[r:!MENTIONS]->(neighbor)
                RETURN node.id + ' - ' + type(r) + ' -> ' + neighbor.id AS output
                UNION ALL
                WITH node
                MATCH (node)<-[r:!MENTIONS]-(neighbor)
                RETURN neighbor.id + ' - ' + type(r) + ' -> ' +  node.id AS output
                }
                RETURN output
                """,
                {"query": self.generate_full_text_query(entity)},
            )
            result += "\n".join([el['output'] for el in response])
        return result
    
    
    def unstructured_retriever(self, question: str) -> str:
        embeddings = OllamaEmbeddings(model=self.model_name)
        os.environ["NEO4J_URI"] = self.url
        os.environ["NEO4J_USERNAME"] = self.user
        os.environ["NEO4J_PASSWORD"] = self.pw
        vector_index = Neo4jVector.from_existing_graph(
            embedding=embeddings,
            search_type="hybrid",
            node_label="Document",
            text_node_properties=["text"],
            embedding_node_property="embedding"
        )
        vector_retriever = vector_index.as_retriever()
        return vector_retriever
    
    def retriever(self, question: str):
        print(f"Search query: {question}")
        structured_data = self.structured_retriever(question)
        # vector_retriever = self.unstructured_retriever(question)
        # unstructured_data = [el.page_content for el in vector_retriever.invoke(question)]
        
        final_data = f"""
            Structured data:
            {structured_data}
        """
        #     unstructured data:
        #     {unstructured_data}
        # """
        print(f"\n-------final_data: \n{final_data}")
        return final_data
        
    def estimate(self, user_question):
        # Extract entities from text
        target_entity = "Person, Job Title, Team、Project "
        class Entities(BaseModel):
            """エンティティに関する情報の識別"""

            names: List[str] = Field(
                ...,
                description=f"文章の中に登場する{target_entity}のエンティティ",
            )
            
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"Extract the {target_entity} entity from the text.",
                ),
                (
                    "human",
                    "Extract information from the following using the specified format, expressed in English."
                    "input: {question}",
                ),
            ]
        )
        llm = OllamaFunctions(model=self.model_name, format="json", temperature=0)
        self.entity_chain = prompt | llm.with_structured_output(Entities)
        
        template = """あなたは優秀なAIです。下記のコンテキストを利用してユーザーの質問に丁寧に答えてください。
            必ず文脈からわかる情報のみを使用して回答を生成してください。
            {context}

            ユーザーの質問: {question}
        """

        prompt = ChatPromptTemplate.from_template(template)
        
        chain = (
            RunnableParallel(
                {
                    "context": lambda input: self.retriever(input),
                    "question": RunnablePassthrough(),
                }
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        
        answer = chain.invoke(user_question)
        print(f"\n-------answer: \n{answer}")
        return answer
        

def main():
    """ 
    Neo4jでGraph RAGを実行
    https://sandeep14.medium.com/running-graphrag-locally-with-neo4j-and-ollama-text-format-371bf88b14b7
    """
    data_path = "./data/data.txt"
    model_name = "llama3"
    
    graph_rag = GraphRAG(model_name)
    user_question = "エンジニア職の給料が100万円の場合、suzukiの給料は？"
    graph_rag.estimate(user_question)
    
    
    

if __name__ == "__main__":
    main()
    
