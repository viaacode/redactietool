#
# disable tests until this package works on our Jenkins/ci.meemoo.be
#

from app.services.suggest.Suggest import Suggest

# sparql-endpoint-fixture>=0.5.0

TEST_ENDPOINT = "https://my.rdfdb.com/repo/sparql"


# def test_instantiation():
#     suggest = Suggest("http://localhost/", "x", "y")
#     assert suggest


# def test_get_concept(sparql_endpoint):
#     # pylint: disable=unused-variable
#     endpoint = sparql_endpoint(  # noqa: F841
#         TEST_ENDPOINT, ["tests/fixture_data/skos.ttl"]
#     )
#     suggest = Suggest(TEST_ENDPOINT, "x", "y")

#     results = list(suggest.get_concept([f"{Suggest.EXT_NS}vak/nederlands"]))
#     assert len(results) == 1
#     assert results[0] == {
#         "definition": "lorem ipsum",
#         "id": f"{suggest.EXT_NS}vak/nederlands",
#         "label": "Nederlands",
#     }


# def test_suggest(sparql_endpoint):
#     # pylint: disable=unused-variable
#     endpoint = sparql_endpoint(  # noqa: F841
#         TEST_ENDPOINT, ["tests/fixture_data/skos.ttl"]
#     )
#     suggest = Suggest(TEST_ENDPOINT, "x", "y")

#     results = list(
#         suggest.suggest(
#             [f"{Suggest.OND_NS}thema/nederlandse-taal"],
#             [f"{Suggest.EXT_NS}structuur/lager-1e-graad"],
#         )
#     )
#     assert len(results) == 1
#     assert results[0] == {
#         "definition": "lorem ipsum",
#         "id": f"{suggest.EXT_NS}vak/nederlands",
#         "label": "Nederlands",
#         "related_id": [
#             "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-1e-graad"
#         ],
#     }


# def test_get_graden(sparql_endpoint):
#     # pylint: disable=unused-variable
#     endpoint = sparql_endpoint(  # noqa: F841
#         TEST_ENDPOINT, ["tests/fixture_data/skos.ttl"]
#     )
#     suggest = Suggest(TEST_ENDPOINT, "x", "y")

#     results = list(suggest.get_graden())
#     assert len(results) == 1
#     assert results[0] == {
#         "definition": "Lager 1ste graad",
#         "id": f"{Suggest.EXT_NS}structuur/lager-1e-graad",
#         "label": "lager 1ste graad",
#         "child_count": 0,
#         "parent_id": f"{suggest.EXT_NS}structuur/lager-onderwijs",
#     }


# def test_get_niveaus(sparql_endpoint):
#     # pylint: disable=unused-variable
#     endpoint = sparql_endpoint(  # noqa: F841
#         TEST_ENDPOINT, ["tests/fixture_data/skos.ttl"]
#     )
#     suggest = Suggest(TEST_ENDPOINT, "x", "y")

#     results = list(suggest.get_niveaus())
#     assert len(results) == 2
#     assert results[0] == {
#         "definition": "Lager onderwijs",
#         "id": f"{Suggest.EXT_NS}structuur/lager-onderwijs",
#         "label": "lager onderwijs",
#         "child_count": 1,
#         "collection": "Onderwijs subniveaus",
#         "parent_id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/basis-onderwijs",
#     }
#     assert results[1] == {
#         "definition": "Kleuteronderwijs",
#         "id": f"{Suggest.EXT_NS}structuur/kleuteronderwijs",
#         "label": "kleuteronderwijs",
#         "child_count": 0,
#         "collection": "Onderwijs subniveaus",
#         "parent_id": "https://w3id.org/onderwijs-vlaanderen/id/structuur/basis-onderwijs",
#     }


# def test_get_themas(sparql_endpoint):
#     # pylint: disable=unused-variable
#     endpoint = sparql_endpoint(TEST_ENDPOINT, ["tests/fixture_data/skos.ttl"])  # noqa: F841
#     suggest = Suggest(TEST_ENDPOINT, "x", "y")

#     results = list(suggest.get_themas())
#     assert len(results) == 2
#     assert results[0] == {
#         "definition": "Taalkunde, exclusief literatuur, voor de Nederlandse taal",
#         "id": f"{Suggest.OND_NS}thema/nederlandse-taal",
#         "label": "Nederlandse taal",
#     }
#     assert results[1] == {
#         "definition": "Alles over rechtbanken, rechtspraak, criminaliteit, wetgeving, ...",
#         "id": f"{suggest.OND_NS}thema/recht",
#         "label": "recht",
#     }


def test_get_children(sparql_endpoint):
    # pylint: disable=unused-variable
    endpoint = sparql_endpoint(  # noqa: F841
        TEST_ENDPOINT, ["tests/fixture_data/skos.ttl"]
    )
    suggest = Suggest(TEST_ENDPOINT, "x", "y")

    results = list(suggest.get_children(
        [f"{suggest.EXT_NS}structuur/lager-onderwijs"]))
    assert len(results) == 2
    assert results[0] == {
        "definition": "Lager 1ste graad",
        "id": f"{Suggest.EXT_NS}structuur/lager-1e-graad",
        "label": "lager 1ste graad",
        "parent_id": f"{Suggest.EXT_NS}structuur/lager-onderwijs",
    }


def test_get_related(sparql_endpoint):
    # pylint: disable=unused-variable
    endpoint = sparql_endpoint(  # noqa: F841
        TEST_ENDPOINT, ["tests/fixture_data/skos.ttl"]
    )
    suggest = Suggest(TEST_ENDPOINT, "x", "y")

    results = list(
        suggest.get_related_vak(
            [
                f"{suggest.EXT_NS}structuur/lager-1e-graad",
                f"{suggest.EXT_NS}structuur/basisonderwijs",
            ]
        )
    )
    assert len(results) == 2
    assert results[0] == {
        "definition": "lorem ipsum",
        "id": f"{Suggest.EXT_NS}vak/nederlands",
        "label": "Nederlands",
        # pylint: disable=line-too-long
        "related_id": [
            "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-1e-graad",
            "https://data.hetarchief.be/id/onderwijs/thema/nederlandse-taal",
            "https://w3id.org/onderwijs-vlaanderen/id/structuur/kleuteronderwijs",
        ],
    }
    assert results[1] == {
        # pylint: disable=line-too-long
        "definition": "Identiteit, diversiteit, ...",
        "id": f"{Suggest.EXT_NS}vak/burgerschap",
        "label": "burgerschap",
        "related_id": [
            "https://w3id.org/onderwijs-vlaanderen/id/structuur/lager-1e-graad",
            "https://data.hetarchief.be/id/onderwijs/thema/recht",
        ],
    }
