from re import L
import requests

from main.app.populate_template import personalise_email

EMAIL_LOCATION = "main/database/email-template.txt"


def inform_nomination(nominator_fullname, 
        nominator_email, nominee_fullname, nominee_email):
    to = nominee_fullname +" <"+nominee_email+">"
    subject = "You have been nominated to collect a package"
    text = """Dear {},\n {} ({}) has nominated you to collect a package for them.\n 
            Please go to collect it.\n If you are unable to collect it please cancel the nomination at
            https://drp11.herokuapp.com/ where you can also view any other parcels 
            you may still need to collect. \nThanks, \n
            The MmmmBoxes Team""".format(nominee_fullname, nominator_fullname, nominator_email)
    return send_message(to,subject,text)

def inform_nomination_cancellation(nominator_fullname, 
        nominator_email, nominee_fullname, nominee_email, nominator_revoked):
    if nominator_revoked:
        inform_nominee_nomination_revoked(nominator_fullname, 
        nominator_email, nominee_fullname, nominee_email)
    else:
        inform_nominator_nomination_cancelled(nominator_fullname, 
        nominator_email, nominee_fullname, nominee_email)

def inform_nominator_nomination_cancelled(nominator_fullname, 
        nominator_email, nominee_fullname, nominee_email):
    to = nominator_fullname +" <"+nominator_email+">"
    subject = "Package collection nomination cancelled"
    text = """Dear {},\n {} ({}) is unable to collect your parcel for you.\n 
            Please consider collecting it yourself or nominate someone else at 
            https://drp11.herokuapp.com/. \nThanks, \nThe MmmmBoxes 
            Team""".format(nominator_fullname, nominee_fullname, nominee_email)
    return send_message(to,subject,text)

def inform_nominee_nomination_revoked(nominator_fullname, nominator_email, nominee_fullname, nominee_email):
    to = nominee_fullname +" <"+nominee_email+">"
    subject = "Package collection nomination revoked"
    text = """Dear {},\n {} ({}) has revoked your nomination to collect their parcel.\n 
            Please do not go to collect it.\n Please visit https://drp11.herokuapp.com/ 
            to view any other parcels you may still need to collect. \nThanks, \n
            The MmmmBoxes Team""".format(nominee_fullname, nominator_fullname, nominator_email)
    return send_message(to,subject,text)

def inform_resident_parcel_arrived(resident_email, resident_name):
    to = resident_name +" <"+resident_email+">"
    subject = "Your parcel has arrived"
    text = """Dear {},\n Your parcel has been received by your front desk staff and is ready for collection.\n Please go to collect it or nominate someone else for collection at https://drp11.herokuapp.com/.\nThanks, \nThe MmmmBoxes Team""".format(resident_name)
    return send_message(to,subject,text)

def send_message(to, subject, text):
    """
    Sends email usage via mailgun API
    example usage:
    to = 'Full Name <email@ic.ac.uk>'
    subject = 'this is the subject'
    text = 'drp11 sent a message to you vial mailgun' 
    """
    return requests.post(
		"https://api.mailgun.net/v3/sandboxc608264d0fa546f3bb2cad9ead57934d.mailgun.org/messages",
		auth=("api", "7f334c44d2d5f3712359685a8d2918ba-77985560-ecb7658e"),
		data={"from": "Mailgun Sandbox <postmaster@sandboxc608264d0fa546f3bb2cad9ead57934d.mailgun.org>",
			"to": to,
			"subject": subject,
			"text": text})

def send_reminder(fullname, email, title, delivered):
    to = fullname + "<"+email+">"
    subject = "Parcel Collection Reminder"
    with open(EMAIL_LOCATION, "r") as f:
        email_template = f.read()
    text = personalise_email(
                email_template,
                full_name=fullname,
                date_d=delivered,
                description=title,
            )
    send_message(to,subject,text)