SELECT item, SUM(qty) AS qty
FROM orders
WHERE status = 'paid'
GROUP BY item
ORDER BY qty DESC
LIMIT 1;
