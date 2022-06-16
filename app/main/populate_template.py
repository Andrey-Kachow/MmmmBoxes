import re

reg_firstname = "(<first-name>)"  # first name of student
reg_lastname = "(<last-name>)"  # surname name of student
reg_date_d = "(<date-d>)"  # date delivered
reg_date_t = "(<date-t>)"  # today's date
reg_urgency = "(<urgency>)"  # urgency level on package
reg_description = "(<description>)"  # description
reg_type = "(<type>)"  # type of package


def replace(text: str, pattern: str, new_text: str) -> str:
    return re.sub(pattern, new_text, text)


def personalise_email(email: str, first_name="", last_name="", date_d="", date_t="", urgency="",
                      description="", type_package="") -> str:
    p_email = email
    p_email = replace(p_email, reg_firstname, first_name)
    p_email = replace(p_email, reg_lastname, last_name)
    p_email = replace(p_email, reg_date_d, date_d)
    p_email = replace(p_email, reg_date_t, date_t)
    p_email = replace(p_email, reg_urgency, urgency)
    p_email = replace(p_email, reg_description, description)
    p_email = replace(p_email, reg_type, type_package)
    return p_email

