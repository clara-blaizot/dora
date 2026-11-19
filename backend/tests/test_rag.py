"""Tests du RAG, sans clé API : Qdrant tourne en mémoire (voir conftest.py)."""

from app.rag import vector_store
from app.rag.pdf import chunk_pages


def test_decoupage_garde_le_numero_de_page():
    pages = ["mot " * 600, "", "court"]
    chunks = chunk_pages(pages, size=1000, overlap=200)

    assert {c.page for c in chunks} == {1, 3}
    assert all(len(c.text) <= 1000 for c in chunks)
    assert chunks[-1].text == "court"


def test_morceaux_tiennent_dans_la_fenetre_du_modele():
    """Le modèle d'embeddings ignore tout ce qui dépasse 128 tokens."""
    from tokenizers import Tokenizer

    from app.rag.embeddings import _model

    # Copie du tokenizer, sans troncature, pour compter les vrais tokens
    tokenizer = Tokenizer.from_str(_model().model.tokenizer.to_str())
    tokenizer.no_truncation()

    cours = (
        "La mitochondrie est un organite intracellulaire entouré d'une double membrane, "
        "présent dans la plupart des cellules eucaryotes. Elle assure la respiration "
        "cellulaire : l'oxydation du glucose et des acides gras y produit de l'adénosine "
        "triphosphate (ATP), principale source d'énergie de la cellule. Le cycle de Krebs "
        "se déroule dans la matrice, tandis que la chaîne respiratoire est localisée dans "
        "la membrane interne, repliée en crêtes. Les mitochondries possèdent leur propre "
        "ADN, circulaire, transmis par la mère."
    )
    for chunk in chunk_pages([cours]):
        assert len(tokenizer.encode(chunk.text).ids) <= 128


def test_recherche_limitee_a_la_matiere():
    from app.rag.pdf import Chunk

    vector_store.index_chunks("cours-bio", "svt", "bio.pdf", [
        Chunk("La mitochondrie produit l'énergie de la cellule sous forme d'ATP.", page=4),
        Chunk("Le noyau contient l'ADN de la cellule.", page=2),
    ])
    vector_store.index_chunks("cours-chimie", "chimie", "chimie.pdf", [
        Chunk("L'ATP est une molécule riche en énergie.", page=7),
    ])

    results = vector_store.search("Quel organite fabrique l'ATP ?", "svt", limit=3)
    assert results[0].page == 4
    assert {r.subject_id for r in results} == {"svt"}

    vector_store.delete_document("cours-bio")
    assert vector_store.search("ATP", "svt") == []


def test_set_subject_deplace_les_morceaux():
    from app.rag.pdf import Chunk

    vector_store.index_chunks("cours", "", "cours.pdf", [Chunk("La photosynthèse.", page=1)])
    vector_store.set_subject("cours", "svt")
    assert vector_store.search("photosynthèse", "svt")[0].document_id == "cours"
