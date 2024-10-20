import os
from dotenv import load_dotenv
import json
from typing import Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone as PineconeClient , Index

load_dotenv()

pc = PineconeClient(api_key="Place_Holder")
index_name = "wardrobe"
index = pc.Index(index_name)

embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

apparel_list = [
    {
        "apparel_id": "apparel_001",
        "gender": "Male",
        "dressing": "Office wear/Casual",
        "season": "Winter, Spring, Summer, or Autumn",
        "occasion": "Office",
        "color": "blue",
        "material": "Cotton",
        "style": "Modern and contemporary styles",
        "apparel_type": "Collared shirts",
        "image_url": "https://st4.depositphotos.com/1007995/22001/i/1600/depositphotos_220018004-stock-photo-relaxed-casual-man-wearing-jeans.jpg"
    },
    {
        "apparel_id": "apparel_002",
        "gender": "Male",
        "dressing": "Casual",
        "season": "All",
        "occasion": "Party",
        "color": "Beige",
        "material": "Cotton",
        "style": "Modern",
        "apparel_type": "Pants",
        "image_url": "https://ksubi.com/cdn/shop/files/JEAN_VanWinkleEarthTones_5048.jpg?v=1696552936&width=600"
    },
    {
        "apparel_id": "apparel_003",
        "gender": "Male",
        "dressing": "Casual",
        "season": "Winter",
        "occasion": "Office",
        "color": "Red",
        "material": "Cotton",
        "style": "Modern",
        "apparel_type": "Shirt",
        "image_url": "https://www.primeporter.com/cdn/shop/products/RedColourCottonShirtForMen-4_large.jpg"
    },
    {
        "apparel_id": "apparel_004",
        "gender": "Male",
        "dressing": "Casual",
        "season": "Autumn",
        "occasion": "Party",
        "color": "Blue and White",
        "material": "Cotton",
        "style": "Checkered",
        "apparel_type": "Shirt",
        "image_url": "https://cdn.staticans.com/image/tr:e-sharpen-01,h-665,w-500,cm-pad_resize/data/Killer/16sep2024/1621-FS-TACTICAL-K071FSSLNDR-NV_1.jpg"
    },
    {
        "apparel_id": "apparel_005",
        "gender": "Male",
        "dressing": "Formal",
        "season": "Any",
        "occasion": "Office",
        "color": "Light Blue",
        "material": "Cotton",
        "style": "Slim fit",
        "apparel_type": "Shirt",
        "image_url": "https://statusquo.in/cdn/shop/products/SQ-SS-22271-SKY_BLUE_0000_1.jpg"
    }
]


def process_product(apparel: Dict[str, Any], embeddings: GoogleGenerativeAIEmbeddings) -> Dict[str, Any]:
    """
    Process a single product and prepare it for insertion into Pinecone.
    """
    text = f"gender: {apparel['gender']}\n"
    text += f"dressing: {apparel['dressing']}\n"
    text += f"season: {apparel['season']}\n"
    text += f"occasion: {apparel['occasion']}\n"
    text += f"color: {apparel['color']}\n"
    text += f"material: {apparel['material']}\n"
    text += f"style: {apparel['style']}\n"
    text += f"apparel_type: {apparel['apparel_type']}\n"

    # text = f"{apparel['gender']}\n"
    # text += f"|{apparel['dressing']}\n"
    # text += f"|{apparel['season']}\n"
    # text += f"|{apparel['occasion']}\n"
    # text += f"|{apparel['color']}\n"
    # text += f"|{apparel['material']}\n"
    # text += f"|{apparel['style']}\n"
    # text += f"|{apparel['apparel_type']}\n"

    embedding = embeddings.embed_query(text)

    metadata = {
        "text": text,
        "gender": apparel['gender'],
        "dressing": apparel['dressing'],
        "season": apparel['season'],
        "occasion": apparel['occasion'],
        "color": apparel['color'],
        "material": apparel['material'],
        "style": apparel['style'],
        "image_url": apparel['image_url']
    }
    apparel_id = apparel['apparel_id']

    return {
        "id": apparel_id,
        "values": embedding,
        "metadata": metadata
    }

def insert_data_into_pinecone(data: Dict[str, Any], index: Index, embeddings: GoogleGenerativeAIEmbeddings):
    """
    Process multiple products and insert them into Pinecone.
    """
    vectors = []
    for apparel_data in data:
        vector = process_product(apparel_data, embeddings)
        vectors.append(vector)

    index.upsert(vectors=vectors)
    print(vectors)
    print(f"Successfully embedded {len(vectors)} products into Pinecone index '{index_name}'")

insert_data_into_pinecone(apparel_list, index, embeddings)
