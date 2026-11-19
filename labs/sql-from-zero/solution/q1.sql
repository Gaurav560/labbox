SELECT id, qty
FROM orders
WHERE item = 'filter coffee' AND status = 'paid' AND outlet_id = 3
ORDER BY id;
