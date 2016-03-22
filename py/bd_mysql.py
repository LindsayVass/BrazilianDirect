import MySQLdb
import pandas as pd
import numpy as np
import ConfigParser

def connect_bd_mysql(config_path):

	# Parse config file
	Config = ConfigParser.ConfigParser()
	Config.read(config_path)
	host = Config.get('credentials', 'host')
	port = int(Config.get('credentials', 'port'))
	user = Config.get('credentials', 'user')
	pw = Config.get('credentials', 'pw')
	db = Config.get('credentials', 'db')

	# Connect to MySQL db
	myDB = MySQLdb.connect(host=host, port=port, user=user, passwd=pw, db=db)

	return(myDB)

def download_quote_data(con):
	# Get quote data
	quote_query = """
	SELECT  q.quote_id, 
	        c.email,
	        sq.title AS quote_status,
	        q.date_created, 
	        DATEDIFF(q.date_needed, q.date_created) AS days_until_needed,
	        CASE WHEN c.phone_home <> ""
	             THEN 1
	             ELSE 0
	             END AS phone_provided,
	        q.ship_state,
	        q.install_subfloor,
	        q.employee_id,
	        ql.sq_ft,
	        ql.cust_price,
	        p.retail_price,
	        s.common_name,
	        p.finish,
	        p.grade,
	        p.milling,
	        p.width,
	        p.construction
	FROM    brazdir_crm.quote q, 
	        brazdir_crm.quote_line_item ql, 
	        brazdir_crm.status_quote sq, 
	        brazdir_crm.product p, 
	        brazdir_crm.species s,
	        brazdir_crm.contact c
	WHERE   q.quote_id = ql.quote_id
	AND     sq.status_quote_id = q.status_id
	AND     ql.product_id = p.product_id
	AND     p.species_id = s.species_id
	AND     q.contact_id = c.contact_id
	;
	"""
	quote_query = quote_query.replace('\n', ' ')

	df = pd.read_sql(quote_query, con)

	return(df)

def pre_process_mysql(df):
	
	# Convert quote_id to int
	df['quote_id'] = df['quote_id'].astype(int)

	# Replace days_until_needed < 1 with np.nan
	df.loc[df['days_until_needed'] < 1, 'days_until_needed'] = np.nan

	# bin days_until needed
	bins = [0, 30, 60, 90, np.nanmax(df['days_until_needed'].values) + 1]
	labels = ['0-30', '31-60', '61-90', '91+']
	df['days_until_needed_bin'] = pd.cut(df['days_until_needed'], bins, labels=labels)

	# bin sq_ft
	bins = [0, 500, 1000, 1500, 2000, 5000, max(df['sq_ft'].values) + 1]
	labels = ['0-500', '501-1000', '1001-1500', '1501-2000', '2001-5000', '5001+']
	df['sq_ft_bin'] = pd.cut(df['sq_ft'], bins, labels=labels)

	# Replace zero values for customer price
	df.loc[df['cust_price'] == 0, 'cust_price'] = np.nan

	# Replace outlier values for customer price with np.nan
	df.loc[df['cust_price'] > 20, 'cust_price'] = np.nan

	# Replace zero values for retail price
	df.loc[df['retail_price'] == 0, 'retail_price'] = np.nanmax

	# Create a column for whether the quote converted
	df['converted'] = np.where(df['quote_status'] == 'Converted', 1, 0)

	# drop quote_status
	df = df.drop('quote_status', axis=1)

	# Drop timestamp from date_created
	df['date_created'] = [x.date() for x in df['date_created']]

	# Create columns for month and year
	df['month'] = [x.month for x in df['date_created']]
	df['year'] = [x.year for x in df['date_created']]

	# Filter out quotes pre-2009
	df = df[df['year'] >= 2009]

	### clean ship_state
	# Change md to MD
	df.loc[df['ship_state'] == 'md', 'ship_state'] = 'MD'

	# Replace -- and '' with MISSING
	df.loc[df['ship_state'] == '', 'ship_state'] = 'MISSING'
	df.loc[df['ship_state'] == '--', 'ship_state'] = 'MISSING'

	### clean install_subfloor
	# Merge missing values with other
	df.loc[df['install_subfloor'] == '', 'install_subfloor'] = 'Other'

	### clean employee_id
	# Merge values into OTHER
	df.loc[~df['employee_id'].isin(['SO', 'NP', 'DC']), 'employee_id'] = 'OTHER'

	### clean common_name
	
	# Crosstabulate species by converted
	xt_species = pd.crosstab(df['common_name'], df['converted']).reset_index()

	# identify species with < 50 conversions
	conversion_thresh = 50
	other_species = list(xt_species.loc[xt_species[1] < conversion_thresh, 'common_name'])

	# merge labels
	df.loc[df['common_name'].isin(other_species), 'common_name'] = 'Other'

	### clean finish
	# relabel Prefinished Natural
	df.loc[df['finish'] == 'Prefinished Natural', 'finish'] = 'Prefinished'

	# label missing data
	df.loc[df['finish'] == '', 'finish'] = 'Missing'

	### clean grade
	# relabel Select
	df.loc[df['grade'] == 'Select', 'grade'] = 'Select & Better'

	# relabel Rustic
	df.loc[df['grade'] == 'Rustic', 'grade'] = 'Missing'

	# relabel empty
	df.loc[df['grade'] == '', 'grade'] = 'Missing'

	### clean milling
	# create missing label
	df.loc[df['milling'] == '', 'milling'] = 'Missing'

	# relabel nan
	df['milling'] = df['milling'].fillna(value = 'Missing')

	### clean width
	df['width'] = [x.strip().replace('"', '') if x is not None and x != '' else np.nan for x in df['width'] ]
	weird_width = ['2 1/4', '4 or 6', '5, 6, 7', '3 5/8', '3,4,5', '5.5, 7', '3 - 8', '3 3/4', '5 1/4', '5,6,7,or 8']
	
	# merge weird widths
	df.loc[df['width'].isin(weird_width), 'width'] = 'Other'

	### clean construction
	# relabel Engineered Click
	df.loc[df['construction'] == 'Engineered Click', 'construction'] = 'Engineered'

	# relabel Solid Long Lengths
	df.loc[df['construction'] == 'Solid Long Lengths', 'construction'] = 'Solid'

	# relabel ''
	df.loc[df['construction'] == '', 'construction'] = 'Missing'

	return(df)
