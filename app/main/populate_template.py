import re

firstname = "(<first-name>)"     # first name of student
lastname = "(<last-name>)"       # surname name of student
date_d = "(<date-d>)"            # date delivered
date_t = "(<date-t>)"            # today's date
urgency = "(<urgency>)"          # urgency level on package
description = "(<description>)"  # description
type = "(<type>)"                # type of package

def replace(text:str, pattern:str, new_text:str) -> str:
    return re.sub(pattern, new_text, text)

