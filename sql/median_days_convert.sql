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