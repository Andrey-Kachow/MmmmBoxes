import re

reg_fullname = "(<full-name>)"  # full name of student
reg_date_d = "(<date-d>)"  # date delivered
reg_date_t = "(<date-t>)"  # today's date
reg_urgency = "(<urgency>)"  # urgency level on package
reg_description = "(<description>)"  # description


def replace(text: str, pattern: str, new_text: str) -> str:
    return re.sub(pattern, new_text, text)


def personalise_email(email: str, full_name="", date_d="", date_t="", urgency="",
                      description="") -> str:
    p_email = email
    p_email = replace(p_email, reg_fullname, full_name)
    p_email = replace(p_email, reg_date_d, date_d)
    p_email = replace(p_email, reg_date_t, date_t)
    p_email = replace(p_email, reg_urgency, urgency)
    p_email = replace(p_email, reg_description, description)
    return p_email


def email_resident(email: str, content: str):
    print("{Emailing resident at " + email + " '" + content + "'}")
