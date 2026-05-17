import pytest
from app.catalog_store import CatalogStore
from app.assessment import Assessment

def test_catalog_loads_successfully():
    store = CatalogStore()

    assert len(store.get_all()) == 377

    opq = store.get_by_name("Occupational Personality Questionnaire OPQ32r")
    assert opq is not None
    assert opq.entity_id == "720"
    assert "Personality & Behavior" in opq.keys

def test_test_type_mapper():
    a1 = Assessment(
        entity_id="1", name="Test1", link="",
        keys=["Knowledge & Skills", "Simulations"]
    )
    assert a1.test_type_codes == "K,S"

    a2 = Assessment(
        entity_id="2", name="Test2", link="",
        keys=["Ability & Aptitude"]
    )
    assert a2.test_type_codes == "A"

def test_validate_url():
    store = CatalogStore()
    opq = store.get_by_name("Occupational Personality Questionnaire OPQ32r")

    assert store.validate_url(opq.link) is True
    assert store.validate_url("https://www.shl.com/products/fake-url") is False
