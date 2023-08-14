"""Chain that calls data stored in a knowledge base created by me

"""
# Imports to connect to Cassandra
from cassandra.cluster import (
    Cluster,
)
from cassandra.auth import PlainTextAuthProvider
#from cqlsession import getCQLSession, getCQLKeyspace

# Imports to manage index data
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader, CSVLoader
from langchain.vectorstores.cassandra import Cassandra
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings

import os
import json
import sys
from dotenv import load_dotenv

from typing import Any, Dict, Optional
from pydantic import BaseModel, Extra, root_validator
from langchain.utils import get_from_dict_or_env

# Load the environment variables 
load_dotenv()
ASTRA_DB_TOKEN_BASED_USERNAME = os.environ["ASTRA_DB_TOKEN_BASED_USERNAME"]
ASTRA_DB_TOKEN_BASED_PASSWORD = os.environ["ASTRA_DB_TOKEN_BASED_PASSWORD"]
ASTRA_DB_SECURE_BUNDLE_PATH = os.environ["ASTRA_DB_SECURE_BUNDLE_PATH"]
ASTRA_DB_KEYSPACE = os.environ["ASTRA_DB_KEYSPACE"]

# Utility functions , likely don't really need this but these were in the Google Colab example 
def getCQLSession(mode='astra_db'):
    if mode == 'astra_db':
        cluster = Cluster(
            cloud={
                "secure_connect_bundle": ASTRA_DB_SECURE_BUNDLE_PATH,
            },
            auth_provider=PlainTextAuthProvider(
                ASTRA_DB_TOKEN_BASED_USERNAME,
                ASTRA_DB_TOKEN_BASED_PASSWORD,
            ),
        )
        astraSession = cluster.connect()
        return astraSession
    else:
        raise ValueError('Unsupported CQL Session mode')

def getCQLKeyspace(mode='astra_db'):
    if mode == 'astra_db':
        return ASTRA_DB_KEYSPACE
    else:
        raise ValueError('Unsupported CQL Session mode')

cqlMode = 'astra_db'
session = getCQLSession(mode=cqlMode)
keyspace = getCQLKeyspace(mode=cqlMode)

os.environ['OPENAI_API_TYPE'] = 'open_ai'
    
llm = OpenAI(temperature=0)
myEmbedding = OpenAIEmbeddings()

# from sentence_transformers import SentenceTransformer
# from typing import List

# from langchain.embeddings import HuggingFaceEmbeddings
# model_name="intfloat/multilingual-e5-small"

# class Embed:
#   def __init__(self):
#         self.transformer = SentenceTransformer(model_name)

#   def __call__(self, text_batch: List[str]):
#       # We manually encode using sentence_transformer since LangChain
#       # HuggingfaceEmbeddings does not support specifying a batch size yet.
#       text = text_batch["item"][0]
#       embeddings = self.transformer.encode(
#           text,
#           batch_size=100 #,  # Large batch size to maximize GPU/CPU utilization.
#           #device="cuda",
#       ).tolist()
#       return {'results': [{"main": zip(text, embeddings), "authors": text_batch["authors"], "title": text_batch['title'], "paper_id": text_batch['paper_id'], "summary": text_batch['summary'], "p_cat": text_batch['primary_category'], "cats": text_batch['categories']}]}

# myEmbedding = Embed()

# reusable get index method to get the index backed by a Cassandra vector store 
def getIndex(name:str):
    table_name = name

    myCassandraVStore = Cassandra(
        embedding=myEmbedding,
        session=session,
        keyspace=keyspace,
        table_name= table_name
    )

    index = VectorStoreIndexWrapper(vectorstore=myCassandraVStore)
    return index


class HiddenPrints:
    """Context manager to hide prints."""
    def __enter__(self) -> None:
        """Open file to pipe stdout to."""
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, *_: Any) -> None:
        """Close file that stdout was piped to."""
        sys.stdout.close()
        sys.stdout = self._original_stdout

class ResearchWrapper(BaseModel):
    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that we can get the Keyspace and Creds via ENV Vars"""
        try:
            cqlMode = 'astra_db'
            session = getCQLSession(mode=cqlMode)
            keyspace = getCQLKeyspace(mode=cqlMode)
        except ImportError:
            raise ValueError(
                "Could not find environment variables for Astra"
                "Please add them to your .env file as instructed."
            )
        return values

    def research_papers(self, query: str) -> str:
        """Get answer from Vector Store with text of research papers"""
        q = query  # str | Search query term or phrase.
        # table_name = 'vector_search'
        table_name = 'papers_new_metadata'
        index = getIndex(table_name)
        with HiddenPrints():
            try:
                # Get Answer
                response = index.query(query, llm=llm)            
            except Exception as e:
                raise ValueError(f"Got error from Cassio / LangChain Index: {e}")
        return response

    def research_papers_summary(self, query: str) -> str:
        """Get answer from Vector Store with text of research papers summary"""
        q = query  # str | Search query term or phrase.
        table_name = 'papers_new_summary'
        index = getIndex(table_name)
        with HiddenPrints():
            try:
                # Get Answer
                response = index.query(query, llm=llm)            
            except Exception as e:
                raise ValueError(f"Got error from Cassio / LangChain Index: {e}")
        return response