import requests
import xml.etree.ElementTree as ET
import re
from langchain.docstore.document import Document
import json
import ast

# Imports to connect to Cassandra
from cassandra.cluster import (
    Cluster,
)
from cassandra.auth import PlainTextAuthProvider

# Imports to manage index data
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.document_loaders import ArxivLoader
from langchain.retrievers import ArxivRetriever
from langchain.vectorstores.cassandra import Cassandra
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings

import os
import json
import sys
from dotenv import load_dotenv

from typing import Any, Dict, Optional

# Load the environment variables 
load_dotenv()
ASTRA_DB_TOKEN_BASED_USERNAME = os.environ["ASTRA_DB_TOKEN_BASED_USERNAME"]
ASTRA_DB_TOKEN_BASED_PASSWORD = os.environ["ASTRA_DB_TOKEN_BASED_PASSWORD"]
ASTRA_DB_SECURE_BUNDLE_PATH = os.environ["ASTRA_DB_SECURE_BUNDLE_PATH"]
ASTRA_DB_KEYSPACE = os.environ["ASTRA_DB_KEYSPACE"]

target_count = 5

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

def create_index(keyspace, table_name, session):
    index_creator = VectorstoreIndexCreator(
        vectorstore_cls=Cassandra,
        embedding=myEmbedding,
        # text_splitter=CharacterTextSplitter(chunk_size=400, chunk_overlap=0),
        text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=80, length_function=len),
        vectorstore_kwargs={
            'session': session,
            'keyspace': keyspace,
            'table_name': table_name,
        },    
    )
    return index_creator

def ingest_paper_metadata(keyspace, table_name, paper_id, session):
    index_creator = create_index(keyspace, table_name, session)
    print(f"Loading data into Vector Store: {table_name}: Started")
    arxiv_retriver = ArxivRetriever(doc_content_chars_max=-1, load_all_available_meta=True).get_relevant_documents(query=paper_id)
    for x in arxiv_retriver:
        page_content = re.sub('[^a-zA-Z0-9 \n\.:{}~!@#$%^&*()+|"?><-=[]\;\,]', '', str(x.page_content))
        page_content = page_content.replace('"','\'').replace("\n"," ")
        metadata = re.sub('[^a-zA-Z0-9 \n\.:{}~!@#$%^&*()+|"?><-=[]\;\,]', '', str(x.metadata)) 
        metadata = metadata.replace('"','\'').replace('\n',' ').replace('\\n',' ').replace("'s ","''s")
        metadata_dic = ast.literal_eval(metadata)
    arxiv_retriver_cleaned = [ Document(page_content= page_content, metadata=metadata_dic)]
    index = index_creator.from_documents(arxiv_retriver_cleaned)

    summary_table = 'papers_new_summary'
    index_creator_summary = create_index(keyspace, summary_table, session)
    summary = metadata_dic.get("Summary")
    summary_doc = [ Document(page_content=summary)]
    index_summary = index_creator_summary.from_documents(summary_doc)
    print(f"Loading data into Vector Store: {table_name}: Done")

def ingest_paper(keyspace, table_name, paper_id, session):
    index_creator = create_index(keyspace, table_name, session)
    print(f"Loading data into Vector Store: {table_name}: Started")
    arxiv_loader = ArxivLoader(query=paper_id, load_max_docs=2, load_all_available_meta=True)
    index = index_creator.from_loaders([arxiv_loader])
    print(f"Loading data into Vector Store: {table_name}: Done")

def get_count(table_name, category, session):
    query = f"""SELECT COUNT(*) as count FROM {table_name} WHERE category = '{category}';"""
    result = session.execute(query)
    return result

def get_paper_id(table_name, category, session):
    query = f"""SELECT paper_id FROM {table_name} WHERE category = '{category}' LIMIT 1;"""
    result = session.execute(query)
    return result

def insert_process(table_name, category, paper_id, session):
    query = f"""INSERT INTO {table_name} (category, paper_id) VALUES ('{category}', '{paper_id}');"""
    result = session.execute(query)

def delete_ids(table_name, category, paper_id, session):
    query = f"""DELETE FROM {table_name} WHERE category = '{category}' and paper_id = '{paper_id}';"""
    result = session.execute(query)

def process_RNDpapers(category="cs.*"):
    import time
    table_name = 'papers_new'
    paper_ids = 'test.paper_ids'
    inprogress_ids = 'test.inprogress_ids'
    processed_papers = 'test.processed_papers'
    process_completed = False
    while not process_completed:
        result = get_count(processed_papers, category, session)
        for row in result:
            processed_count = row.count
        
        result = get_count(inprogress_ids, category, session)
        for row in result:
            inprogress_count = row.count

        if (processed_count + inprogress_count) >= target_count:
            print("Processing completed. Generated " + str(target_count) + " vectors")
            process_completed = True
            exit(0)

        paper_id = '0'
        result = get_paper_id(paper_ids, category, session)
        for row in result:
            paper_id = row.paper_id

        if (paper_id != '0'):
            print("Processing ", paper_id)
            insert_process(inprogress_ids, category, paper_id, session)
            delete_ids(paper_ids, category, paper_id, session)

            # Do Processing
            target_table = 'papers_new_metadata'
            ingest_paper_metadata(keyspace, target_table, paper_id, session)

            # target_table = 'papers_new'
            # ingest_paper(keyspace, target_table, paper_id, session)

            insert_process(processed_papers, category, paper_id, session)
            delete_ids(inprogress_ids, category, paper_id, session)
        else:
            print("Waiting for paper id to be populated in ", paper_ids)
            time.sleep(10)

def get_ids(start, max_results=30, category="cs.*"):
    url = f'http://export.arxiv.org/api/query?search_query={category}&start={start}&max_results={max_results}'
    # url = f'http://export.arxiv.org/api/query?search_query=1901.01341'
    print(url)
    resp = requests.get(url)
    if resp.status_code == 403:
        raise Exception("Unauthorized! breaking")
    root = ET.fromstring(resp.text)
    ns = { 'r':'http://www.w3.org/2005/Atom'}
    entries = root.findall('r:entry', namespaces=ns)
    all_paper_ids = dict()
    sep = 'v' # delete versions
    for entry in entries:
        for elt in entry:
            if "primary_category" in elt.tag:
                prim_category = elt.attrib["term"]
                if prim_category == 'cs.LG':
                    entry_p = entry[0].text.split("/")
                    all_paper_ids[entry_p[-1].split(sep, 1)[0]] = entry_p[-2]
    return all_paper_ids

def get_paper_ids(category="cs.*"):
    # Execute the code to upload data
    loading_completed = False
    loop_count = 0
    max_results = 30
    paper_ids = 'test.paper_ids'
    process_track = 'test.process_track'
    processed_papers = 'test.processed_papers'
    count = 0
    while not loading_completed:
        start_count = max_results * loop_count + 1
        ids_list = get_ids(start_count, max_results,)
        loop_count = loop_count + 1
        for id in ids_list:
            query = f"""INSERT INTO {paper_ids} (category, paper_id) VALUES ('{category}', '{id}');"""
            try:
                session.execute(query)
            except Exception as e:
                print("Error : statement ", query, " reason ", str(e))
        rows_processed = max_results * loop_count
        query = f"""INSERT INTO {process_track} (category, rows_processed) VALUES ('{category}', {rows_processed});"""
        session.execute(query)

        query = f"""SELECT COUNT(*) FROM {processed_papers} WHERE category = '{category}';"""
        result = session.execute(query)
        for row in result:
            processed_count = row.count

        query = f"""SELECT COUNT(*) FROM {paper_ids} WHERE category = '{category}';"""
        result = session.execute(query)
        for row in result:
            pending_count = row.count

        if (processed_count + pending_count) >= target_count:
            loading_completed = True

if __name__ == "__main__":
    process_RNDpapers()
    # get_paper_ids()