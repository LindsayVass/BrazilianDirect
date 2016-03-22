import bd_mysql

### Connect to MySQL db ###

config_path = '/Users/lindsay/Documents/Data Science/BrazilianDirect/cfg/mysql.cfg'
myDB = bd_mysql.connect_bd_mysql(config_path)

cursor = myDB.cursor()

### Run Query ###

# Get google click id, payment status, payment date, and payment amount
# for orders paid in full in the last 90 days
query = """
SELECT q.gclid, s.description, p.date_modified, p.amount
FROM brazdir_crm.quote q, brazdir_crm.orders o, brazdir_crm.order_payment p, brazdir_crm.status_payment s
WHERE gclid <> ''
AND q.date_created >= NOW() - INTERVAL 90 DAY
AND q.quote_id = o.quote_id
AND o.inv_num = p.inv_num
AND o.status_payment_id = s.status_payment_id
AND s.description = 'Paid In Full';
"""

query = query.replace('\n', ' ')

cursor.execute(query)

results = cursor.fetchall()


### Write to CSV ###
import csv
import datetime

# name output file with today's date
now = datetime.datetime.now()
now = now.strftime("%Y-%m-%d")
filename = '/Users/lindsay/Desktop/offline_conversions_' + now + '.csv'

with open(filename, 'wb') as csvfile:
	csvwriter = csv.writer(csvfile, delimiter = ',')

	# write header
	csvwriter.writerow(['Parameters:EntityType=OFFLINECONVERSION;TimeZone=-0700;'])
	csvwriter.writerow(['Google Click Id', 'Conversion Name', 'Conversion Time', 'Conversion Value', 'Conversion Currency'])

	# write data rows
	for row in results:
		csvwriter.writerow([row[0], row[1], row[2].strftime("%Y-%m-%d %H:%M:%S"), str(row[3])])
