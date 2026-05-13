from app.store import PlatformStore


def test_audit_hash_chain_links_records():
    store = PlatformStore()
    first = store.audit_action("one", "resource-1", "success", "tester")
    second = store.audit_action("two", "resource-2", "success", "tester")

    assert first.previous_hash == "0" * 64
    assert second.previous_hash == first.hash
    assert len(second.hash) == 64

