## Downloading and Uploading Document Sources


## Getting a Vector Database / Account in Astra

If you want to store vast amounts of your data and talk to it, you need to get a vector database setup. Read up on [CassIO's Start Here](https://cassio.org/start_here/) page. 
Make sure you can run the [Colab Notebook](http://colab.research.google.com/github/CassioML/cassio-website/blob/main/docs/frameworks/langchain/.colab/colab_qa-basic.ipynb)


# Download Data 

- FDIC Failed Bank List - https://catalog.data.gov/dataset/fdic-failed-bank-list / https://www.fdic.gov/bank/individual/failed/banklist.csv
    `curl -L https://www.fdic.gov/bank/individual/failed/banklist.csv --output banklist.csv`
- The Cask of Amontillado - https://raw.githubusercontent.com/CassioML/cassio-website/main/docs/frameworks/langchain/texts/amontillado.txt 
    `curl https://raw.githubusercontent.com/CassioML/cassio-website/main/docs/frameworks/langchain/texts/amontillado.txt --output amontillado.txt`

```
cd data/documents
curl -L https://www.fdic.gov/bank/individual/failed/banklist.csv --output banklist.csv
curl https://raw.githubusercontent.com/CassioML/cassio-website/main/docs/frameworks/langchain/texts/amontillado.txt --output amontillado.txt
cd ../..
```


Make sure you add all your API Keys in the .env file. Then you can upload the data to the database. This uses the same concepts in the Google Colab notebook, but it's structured so that we can easily separate the upload and retrieval. 


```
cd /workspace/iris/
python utils/knowledge.py
```

After this is working we can add our tool to our `chainlit.py` file and see if it can answer questions. 

```
        Tool(
            name="FailedBankList",
            func=knowledge.banks,            
            description="useful for when you need to find information about failed banks. the input should either names of banks or the years to see if there are matches. "
        ),   
        Tool(
            name="AmontilladoText",
            func=knowledge.amontillado,
            return_direct=True,
            description="useful for when you need to answer literary questions about The Cask of Amontillado, a short story by Edgar Alan Poe. This uses a vector similarity search. You should ask targeted questions to find similar documents. Input should be a query, and output will be an answer which you should summarize and give back relevant information."
        ) 

```


