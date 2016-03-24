import pandas as pd 

def process_mailchimp(csv_path):
	mail = pd.read_csv(csv_path)
	mail['CONFIRM_TIME'] = pd.to_datetime(mail['CONFIRM_TIME'])
	first_email = min(mail['CONFIRM_TIME'])

	mail = mail.drop(mail.columns[1:], axis=1)
	mail['mail_chimp'] = 1
	mail.columns = ['email', 'mail_chimp']

	return((mail, first_email))
	