import pandas as pd 
import csv
import bd_mysql

### Connect to MySQL db ###

config_path = '/Users/lindsay/Documents/Data Science/BrazilianDirect/cfg/mysql.cfg'
myDB = bd_mysql.connect_bd_mysql(config_path)

cursor = myDB.cursor()

cursor = myDB.cursor()

# Run query to determine median days to conversion
query_median_days = """
SELECT days_to_convert AS median_days_to_convert, row_number
FROM 
	(SELECT sub.days_to_convert, @rownum:=@rownum+1 as row_number
	FROM
		(SELECT s.description,q.date_created, p.date_modified, p.amount, DATEDIFF(p.date_modified, q.date_created) AS days_to_convert
		FROM brazdir_crm.quote q, brazdir_crm.orders o, brazdir_crm.order_payment p, brazdir_crm.status_payment s
		WHERE q.quote_id = o.quote_id
		AND o.inv_num = p.inv_num
		AND o.status_payment_id = s.status_payment_id
		AND p.amount > 750
		ORDER BY DATEDIFF(p.date_modified, q.date_created)
		) sub, (SELECT @rownum:=0) r
        ) sub2
HAVING row_number = (SELECT MAX(row_number) / 2 FROM (SELECT sub.days_to_convert, @rownum:=@rownum+1 as row_number
						FROM
							(SELECT s.description,q.date_created, p.date_modified, p.amount, DATEDIFF(p.date_modified, q.date_created) AS days_to_convert
							FROM brazdir_crm.quote q, brazdir_crm.orders o, brazdir_crm.order_payment p, brazdir_crm.status_payment s
							WHERE q.quote_id = o.quote_id
							AND o.inv_num = p.inv_num
							AND o.status_payment_id = s.status_payment_id
							AND p.amount > 750
							ORDER BY DATEDIFF(p.date_modified, q.date_created)
							) sub, (SELECT @rownum:=0) r
							) sub2)
;
"""
query_median_days = query_median_days.replace('\n', ' ')

cursor.execute(query_median_days)
result = cursor.fetchall()
median_days_to_convert = result[0][0]

# Run query to determine daily revenue
query_revenue = """
SELECT DATE(p.date_entered) as date, SUM(p.amount) as total_revenue
	FROM brazdir_crm.orders o, brazdir_crm.order_payment p
	WHERE o.inv_num = p.inv_num
	GROUP BY 1
	ORDER BY 1;
"""

query_revenue = query_revenue.replace('\n', ' ')

cursor.execute(query_revenue)
result = cursor.fetchall()

d = {'date': [x[0] for x in result],
	 'total_revenue': [x[1] for x in result]}

daily_revenue = pd.DataFrame(d)

# Load daily ad spend from csv (output by AdWords)
filepath = '/Users/lindsay/Documents/Data Science/BrazilianDirect/csv/daily_ad_spend.csv'
daily_ads = pd.read_csv(filepath, sep = ',', skiprows = 1, header = 0, skipfooter = 1, engine = 'python')


