"""
tests/test_rag.py
Unit tests for agricultural case construction, embeddings, and FAISS vector store.
"""

import pytest
import numpy as np
import pandas as pd
from app.rag.document_processor import build_case_text, build_case_metadata
from app.rag.embeddings import embedding_service
from app.rag.vector_store import FAISSVectorStore

def test_document_processor():
    row = pd.Series({
        "Crop": "Rice",
        "Crop_Year": 2020,
        "Season": "Kharif",
        "State": "Andhra Pradesh",
        "Area": 1200.0,
        "Production": 4560.0,
        "Yield": 3.8,
        "Fertilizer": 130.0,
        "Pesticide": 1.1,
        "N": 80.0,
        "P": 40.0,
        "K": 40.0,
        "pH": 6.5,
        "Temperature": 28.0,
        "Rainfall": 1200.0,
        "Humidity": 75.0,
        "NPK_Total": 160.0
    })
    text = build_case_text(row, "CASE_TEST_01")
    meta = build_case_metadata(row, "CASE_TEST_01")

    assert "Case ID: CASE_TEST_01" in text
    assert "Rice" in text
    assert "Andhra Pradesh" in text
    assert meta["case_id"] == "CASE_TEST_01"
    assert meta["yield_val"] == 3.8

def test_embedding_service_dimension_and_norm():
    texts = ["Rice cultivation in Andhra Pradesh", "Wheat farming in Punjab"]
    vecs = embedding_service.encode(texts)
    assert vecs.shape == (2, embedding_service.get_embedding_dim())
    # Verify L2 unit norm
    norms = np.linalg.norm(vecs, axis=1)
    for norm in norms:
        assert norm == pytest.approx(1.0, rel=1e-4)

def test_vector_store_add_and_search():
    vs = FAISSVectorStore(dim=embedding_service.get_embedding_dim())
    texts = ["Rice in Andhra Pradesh", "Wheat in Punjab", "Cotton in Gujarat"]
    metadatas = [
        {"case_id": "C1", "crop": "Rice", "state": "Andhra Pradesh"},
        {"case_id": "C2", "crop": "Wheat", "state": "Punjab"},
        {"case_id": "C3", "crop": "Cotton", "state": "Gujarat"}
    ]
    vecs = embedding_service.encode(texts)
    vs.add_documents(vecs, metadatas, texts)

    q_vec = embedding_service.encode(["Paddy rice farming"])
    results = vs.search(q_vec, top_k=2)

    assert len(results) == 2
    top_meta, score, top_text = results[0]
    assert "case_id" in top_meta
    assert 0.0 <= score <= 1.0
