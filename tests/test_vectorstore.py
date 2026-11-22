"""Tests for the JSON-backed example store."""

from src.ingestion.loader import Document
from src.retrieval.vectorstore import SimpleStore


def _doc(doc_id, content, bambda_type="VIEW_FILTER", description=""):
    return Document(
        id=doc_id,
        content=content,
        metadata={"bambda_type": bambda_type, "bambda_name": doc_id, "description": description},
    )


def test_add_and_count(tmp_path):
    store = SimpleStore(data_dir=tmp_path)
    store.add_bambdas([_doc("a", "jwt token in cookies")])
    assert store.get_bambda_count() == 1


def test_adding_the_same_id_twice_does_not_duplicate(tmp_path):
    store = SimpleStore(data_dir=tmp_path)
    doc = _doc("a", "jwt token in cookies")
    store.add_bambdas([doc])
    store.add_bambdas([doc])
    assert store.get_bambda_count() == 1


def test_data_survives_a_reload(tmp_path):
    SimpleStore(data_dir=tmp_path).add_bambdas([_doc("a", "jwt token")])
    assert SimpleStore(data_dir=tmp_path).get_bambda_count() == 1


def test_search_ranks_the_matching_example_first(tmp_path):
    store = SimpleStore(data_dir=tmp_path)
    store.add_bambdas([
        _doc("jwt", "decode the jwt token from the authorization header", description="jwt"),
        _doc("csp", "check the content security policy header", description="csp"),
    ])
    results = store.search_bambdas("jwt token", n_results=2)
    assert results[0]["id"] == "jwt"
    assert results[0]["score"] > results[1]["score"]


def test_type_filter_excludes_other_types(tmp_path):
    store = SimpleStore(data_dir=tmp_path)
    store.add_bambdas([
        _doc("f", "filter", bambda_type="VIEW_FILTER"),
        _doc("c", "column", bambda_type="CUSTOM_COLUMN"),
    ])
    results = store.search_bambdas("anything", n_results=5, bambda_type="CUSTOM_COLUMN")
    assert len(results) == 1
    assert results[0]["metadata"]["bambda_type"] == "CUSTOM_COLUMN"


def test_clear_empties_the_store(tmp_path):
    store = SimpleStore(data_dir=tmp_path)
    store.add_bambdas([_doc("a", "x")])
    store.clear()
    assert store.get_bambda_count() == 0
