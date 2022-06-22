from main.app.ocr import *
from test.decorators import with_temp_psql_conn

read_data_from_james_bond = """
FBA Box.1 of 1 - 1lb

SHIP FROM: SHIP TO:

James Bond FBA: dnest+sta012

333 Boren Ave N Amazon.com Services, Inc.
Seattle, WA 98109 4255 Anson Blvd

United States Whitestown, IN 46075-4412

United States

FBA (10/30/19 10:55 AM) - 1

FBA15JD9C5R9U000001 ee
|

Mixed SKUs
KM-SSHL-KJON
Qty 1

PLEASE LEAVE THIS LABEL UNCOVERED
"""

read_data_jim_clark = '''
US POSTAGE & FEES PAID 062S0017063017
PRIORI >
eR FROM 90245
COMMERCIAL BASE PRICING

ees i

PRIORITY MAIL 2-DAY™

Stamps.com
1990 E. Grand Ave 0022

El Segundo CA 90245

SHIP = Jim Clark
TO:

123 Chapman Lane
Lotus CA 95651
WadeslalaelDecedelesesllsdeell

USPS TRACKING #

9999 9999 9999 9999 9999 99

Thanks for Shopping with Us!
'''

read_data_jack_ship = '''
US POSTAGE AND FEES PAID
FIRST-CLASS

‘Apr 12 2016

Mailed from ZIP 77024

Son Frat Clase Pag Sve

CommeriatbatePrice 071500856161
USPS FIRST-CLASS PKG

WAREHOUSE 2
11919 WINK RD
HOUSTON 1X 77024-7134

Order: 286

JACK SHIP
609 CASTLE RIDGE RD
AUSTIN TX 78746-5147

USPS TRACKING #

9400 1102 0079 3961 8936 91
'''

read_data_john_amburn = '''
From:

JERRY GUZI

BURRIS COMPUTER FORMS.
2222 ELECTRIC RD

SUITE 204

ROANOKE, VA 24018,

SHIP TO:

JOHN AMBURN
BURRIS COMPUTER FORMS
751 UNION ST

SALEM, VA 24153
'''


def test_nice_read_heading():
    assert nice_read_heading(read_data_from_james_bond)
    assert nice_read_heading(read_data_jim_clark)
    assert nice_read_heading(read_data_jack_ship)
    assert not nice_read_heading(read_data_john_amburn)


def test_titled_as_from_whatever():
    assert titled_as_from_whatever("", None) is None
    assert titled_as_from_whatever(read_data_from_james_bond, "dnest+sta012") == "From James Bond FBA: dnest+sta012"
    assert titled_as_from_whatever(read_data_john_amburn, "John Amburn") == "From JERRY GUZI"

    # Those identify the current wished behaviour in mind, though may not look like ones
    assert titled_as_from_whatever(read_data_jim_clark, "Jim Clark") == "From COMMERCIAL BASE PRICING"
    assert titled_as_from_whatever(read_data_jack_ship, "Jack Ship") == "From Son Frat Clase Pag Sve"


@with_temp_psql_conn
def test_parse_read_data(conn):

    name, title = parse_read_data(conn, "sad input")
    assert name is None
    assert title is None

    register_new_user(conn, "dnest+sta012", "email", "username", "password_plain", False)
    register_new_user(conn, "John Amburn", "email", "username", "password_plain", False)
    register_new_user(conn, "Jim Clark", "email", "username", "password_plain", False)
    register_new_user(conn, "Jack Ship", "email", "username", "password_plain", False)

    name, title = parse_read_data(conn, read_data_from_james_bond)
    assert name == "dnest+sta012"
    assert title == "From James Bond FBA: dnest+sta012"

    name, title = parse_read_data(conn, read_data_jim_clark)
    assert name == "Jim Clark"
    assert title == "US POSTAGE & FEES PAID 062S0017063017"

    name, title = parse_read_data(conn, read_data_jack_ship)
    assert name == "Jack Ship"
    assert title == "US POSTAGE AND FEES PAID"

    name, title = parse_read_data(conn, read_data_john_amburn)
    assert name == "John Amburn"
    assert title == "From JERRY GUZI"
