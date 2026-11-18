SELECT id, qty
FROM orders
WHERE item = 'masala chai' AND status = 'paid' AND outlet_id = 3
ORDER BY id;
