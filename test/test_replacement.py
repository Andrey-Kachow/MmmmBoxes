from app.main.populate_template import replace

def test_replace():
    assert replace("Hello <abc>!", "(<abc>)", "World") == "Hello World!"