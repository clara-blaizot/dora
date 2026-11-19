from fastapi.testclient import TestClient

from app.main import app
from app.services import chat as chat_service
from app.services import documents as documents_service
from app.services import subjects as subjects_service
from conftest import make_pdf

client = TestClient(app)


def _creer_matiere(name):
    r = client.post("/subjects", json={"name": name, "color": "#F783AC"})
    assert r.status_code == 201
    return r.json()["id"]


def _importer(subject_id, filename, pages):
    r = client.post(
        f"/subjects/{subject_id}/documents",
        files=[("files", (filename, make_pdf(pages), "application/pdf"))],
    )
    assert r.status_code == 200, r.text
    return r.json()[0]


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_crud_matieres():
    subject_id = _creer_matiere("Physique")
    assert [s["name"] for s in client.get("/subjects").json()] == ["Physique"]

    r = client.patch(f"/subjects/{subject_id}", json={"name": "Physique quantique"})
    assert r.json() == {"id": subject_id, "name": "Physique quantique", "color": "#F783AC"}

    assert client.delete(f"/subjects/{subject_id}").status_code == 204
    assert client.get("/subjects").json() == []


def test_couleur_invalide_refusee():
    r = client.post("/subjects", json={"name": "Maths", "color": "rouge"})
    assert r.status_code == 422


def test_matiere_inconnue():
    assert client.post("/subjects/inexistante/ask", json={"question": "?"}).status_code == 404
    assert client.get("/subjects/inexistante/documents").status_code == 404
    assert client.patch("/subjects/inexistante", json={"name": "x"}).status_code == 404


def test_upload_refuse_non_pdf():
    subject_id = _creer_matiere("Maths")
    r = client.post(
        f"/subjects/{subject_id}/documents",
        files=[("files", ("notes.txt", b"hello", "text/plain"))],
    )
    assert r.status_code == 400


def test_dora_ne_repond_qu_avec_les_cours_de_la_matiere(monkeypatch):
    physique = _creer_matiere("Physique")
    maths = _creer_matiere("Maths")
    doc_physique = _importer(physique, "meca.pdf", ["La force est egale a la masse fois l'acceleration."])
    _importer(maths, "suites.pdf", ["Une suite de Cauchy converge dans R."])

    assert [d["id"] for d in client.get(f"/subjects/{physique}/documents").json()] == [doc_physique["id"]]

    monkeypatch.setattr(chat_service, "create_message", lambda **k: "Réponse [1]")
    r = client.post(f"/subjects/{physique}/ask", json={"question": "Qu'est-ce qu'une suite de Cauchy ?"})

    assert r.status_code == 200
    sources = r.json()["sources"]
    assert sources, "la matière contient un PDF : il doit y avoir des sources"
    # Même pour une question de maths, seuls les cours de physique sont utilisés
    assert {s["filename"] for s in sources} == {"meca.pdf"}


def test_supprimer_matiere_supprime_ses_pdf():
    physique = _creer_matiere("Physique")
    doc = _importer(physique, "meca.pdf", ["La force est egale a la masse fois l'acceleration."])

    client.delete(f"/subjects/{physique}")

    assert client.get("/documents").json() == []
    assert client.get(f"/documents/{doc['id']}/pdf").status_code == 404


def test_migration_des_pdf_sans_matiere():
    # Un PDF importé avant l'existence des matières n'a pas de subject_id
    doc = documents_service.add_document("", "ancien.pdf", make_pdf(["Ancien cours de chimie."]))

    with TestClient(app):  # déclenche le démarrage, donc la migration
        pass

    (matiere,) = subjects_service.list_subjects()
    assert matiere.name == "Mes cours"
    assert documents_service.list_documents(matiere.id)[0].id == doc.id
    assert chat_service.vector_store.search("chimie", matiere.id)[0].document_id == doc.id
