SELECT o.name, SUM(r.amount_paise) AS revenue_paise
FROM orders r
JOIN outlets o ON o.id = r.outlet_id
WHERE r.status = 'paid'
GROUP BY o.name
ORDER BY revenue_paise DESC;
