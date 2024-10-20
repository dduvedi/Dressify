import os
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Pinecone
from langchain.prompts import PromptTemplate
from pinecone import Pinecone as PineconeClient
import json

from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from flask import Flask, request, jsonify

app = Flask(__name__)
app = FastAPI()
class QueryInput(BaseModel):
    text: str
    brandName: str

@app.post("/outfitsuggestions/")
def fetch_cross_sell_info(requestBody: QueryInput):
    pc = PineconeClient(api_key="f9cd0fd2-8bf1-43a7-a3a2-41e50462b5f0")
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-pro"
    )
    product_info_index_name = "wardrobe"
    product_info_index = pc.Index(product_info_index_name)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Pinecone(product_info_index, embeddings.embed_query, text_key="text")

    docs = vectorstore.similarity_search(requestBody.text, k=5)
    print(docs)
    products = []
    for doc in docs:
        try:
            metadata = doc.metadata
            product_info = {}

            product_info["gender"] = metadata.get('gender', 'Unnamed')
            product_info["dressing"] = metadata.get('dressing', 'No introduction available')
            product_info["season"] = metadata.get('season', 'No description')
            product_info["occasion"] = metadata.get('occasion', 'No description')
            product_info["color"] = metadata.get('color', 'No description')
            product_info["material"] = metadata.get('material', 'No description')
            product_info["style"] = metadata.get('style', 'No description')
            product_info["image_url"] = metadata.get('image_url', 'No description')

            products.append(product_info)

        except json.JSONDecodeError:
            print("Error decoding JSON for product properties")
            pass
    return {
        "products": products
    }


# print(fetch_cross_sell_info("red"))