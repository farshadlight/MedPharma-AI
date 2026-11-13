from app import fetch_fda_drug_info

def test_fda_fetch_callable():
    assert callable(fetch_fda_drug_info)
