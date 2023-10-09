from main.app.populate_template import *


def test_replace():
    assert replace("Hello <abc>!", "(<abc>)", "World") == "Hello World!"


def test_personalise_email():
    assert (
        personalise_email(
            "Hello <full-name>. You have a package. Urgency = <urgency>",
            full_name="Dave",
            urgency=str(5),
        )
        == "Hello Dave. You have a package. Urgency = 5"
    )
