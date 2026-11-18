-- The query the checkout page runs for every order: the customer's 20 latest orders
-- (to show loyalty points). Customer 4242 is a regular at the Andheri outlet.
SELECT id, item, amount_paise, created_at
FROM orders
WHERE customer_id = 4242
ORDER BY created_at DESC
LIMIT 20;
