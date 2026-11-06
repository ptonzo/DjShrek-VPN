from app.nodes import DEFAULT_NODES

def test_five_global_nodes_are_defined():
    assert [node.id for node in DEFAULT_NODES] == ["de-1", "fi-1", "nl-1", "pl-1", "us-1"]
    assert len({node.id for node in DEFAULT_NODES}) == 5
