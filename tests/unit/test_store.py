from cabbage import store, testing


def test_load_store_from_path():
    store_class = store.load_store_from_path("cabbage.testing.InMemoryJobStore")

    assert store_class is testing.InMemoryJobStore
