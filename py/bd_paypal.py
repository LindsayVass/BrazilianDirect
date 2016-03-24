import os
import pandas as pd 

def process_paypal(csv_dir):
	csv_files = [os.path.join(csv_dir, x) for x in os.listdir(csv_dir)]
	paypal = pd.concat((pd.read_csv(f) for f in csv_files))
	paypal.columns = [x.strip() for x in paypal.columns]
	paypal['Date'] = pd.to_datetime(paypal['Date'])
	first_sample = min(paypal['Date'])

	# keep only sample purchases
	paypal = paypal.loc[paypal['Item Title'] == 'Hardwood Flooring Samples', :]
	paypal = pd.DataFrame(paypal['From Email Address'])
	paypal = paypal.drop_duplicates()
	paypal['samples'] = 1
	paypal.columns = ['email', 'samples']

	return(paypal, first_sample)