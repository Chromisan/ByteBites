import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import DataFrameLoader
from langchain_community.vectorstores import FAISS
import numpy as np
import time

# ========== 数据加载与处理 ==========
DATASET_PATH = os.path.join(os.path.dirname(__file__), "restaurant_all.csv")
FAISS_REVIEWS_PATH_COSINE = os.path.join(os.path.dirname(__file__), "faiss_index_cosine")
FAISS_INDEX_NAME = "index"
FAISS_DISTANCE_STRATEGY_COSINE = "COSINE_DISTANCE"

def get_documents(content_func=lambda row: row['name'] + '\n' + row['tag'],
                  metadata_fields=[]):
    """加载并处理餐厅数据，生成文档对象"""
    dataset_df = pd.read_csv(DATASET_PATH)
    dataset_df.drop_duplicates(inplace=True)
    dataset_df['page_content'] = dataset_df.apply(content_func, axis=1)
    metadata_fields = list(set(metadata_fields + ['page_content']))
    loader = DataFrameLoader(dataset_df[metadata_fields], page_content_column='page_content')
    return loader.load()

def content_func(row) -> str:
    """生成每家店铺的完整信息字符串"""
    content_fields = [
        "name", "address", "type", "tag", 
        "cost", "rating", "opentime_today", "opentime_week"
    ]
    rating_fields = [
        "dp_rating", "dp_taste_rating", "dp_env_rating",
        "dp_service_rating", "dp_comment_num"
    ]
    comment_fields = [
        "dp_recommendation_dish", "dp_comment_keywords",
        "dp_top3_comments"
    ]
    info_parts = []
    for field in content_fields:
        if pd.notna(row[field]):
            info_parts.append(f"{field}={row[field]}")
    rating_info = []
    for field in rating_fields:
        if pd.notna(row[field]):
            rating_info.append(f"{field}={row[field]}")
    if rating_info:
        info_parts.append("评分信息:\n" + "\n".join(rating_info))
    if pd.notna(row.get("dp_recommendation_dish")):
        info_parts.append(f"推荐菜: {row['dp_recommendation_dish']}")
    if pd.notna(row.get("dp_comment_keywords")):
        info_parts.append(f"评论关键词: {row['dp_comment_keywords']}")
    if pd.notna(row.get("dp_top3_comments")):
        info_parts.append("精选评论:\n" + row['dp_top3_comments'].replace("|", "\n"))
    return '\n'.join(info_parts)

def get_vector_database(documents, embedding_model, distance_strategy):
    vector_database = FAISS.from_documents(
        documents, embedding_model,
        distance_strategy=distance_strategy
    )
    return vector_database

def init_vectordb():
    print("开始初始化向量数据库...")
    
    # 设置嵌入模型
    embedding_model = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh",
        model_kwargs={"device": "cpu"},
        encode_kwargs={
            "normalize_embeddings": True,
            "batch_size": 16
        }
    )
    
    # 加载文档数据
    metadata_fields = [
        "location", "opentime_week",
        "dp_rating", "dp_taste_rating", "dp_env_rating",
        "dp_service_rating", "dp_comment_num"
    ]
    documents = get_documents(content_func, metadata_fields=metadata_fields)
    print(f"成功加载 {len(documents)} 条餐厅数据")

    # 分批构建向量库
    doclen = len(documents)
    for batch in range(doclen//100 + 1):
        docs = documents[batch*100:(batch+1)*100]
        if batch == 0:
            vector_db = get_vector_database(docs, embedding_model, FAISS_DISTANCE_STRATEGY_COSINE)
        else:
            vector_db.merge_from(get_vector_database(docs, embedding_model, FAISS_DISTANCE_STRATEGY_COSINE))
        print(f"处理进度: {min((batch+1)*100, doclen)}/{doclen}")
        time.sleep(1)  # 可适当缩短等待时间

    # 保存向量库
    vector_db.save_local(folder_path=FAISS_REVIEWS_PATH_COSINE, index_name=FAISS_INDEX_NAME)
    print(f"向量数据库已保存到: {FAISS_REVIEWS_PATH_COSINE}")

if __name__ == "__main__":
    init_vectordb()
