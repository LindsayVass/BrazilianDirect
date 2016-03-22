SELECT DATE(p.date_entered) as date, SUM(p.amount) as total_revenue
	FROM brazdir_crm.orders o, brazdir_crm.order_payment p
	WHERE o.inv_num = p.inv_num
	GROUP BY 1
	ORDER BY 1;