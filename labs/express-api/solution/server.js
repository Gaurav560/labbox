// Dabba Express order tracking API. Start it with: node server.js  (then open the Preview tab)
const express = require("express");

const app = express();
app.use(express.json());

const ORDERS = {
  1: { id: 1, items: ["veg thali", "curd rice"], area: "Baner", status: "out for delivery" },
  2: { id: 2, items: ["dal rice"], area: "Aundh", status: "delivered" },
};
let nextId = 3;

app.get("/", (req, res) => {
  res.json({ service: "dabba-express", orders: Object.keys(ORDERS).length });
});

app.get("/orders/:id", (req, res) => {
  const order = ORDERS[req.params.id];
  if (!order) return res.status(404).json({ error: `No order ${req.params.id}` });
  res.json(order);
});

app.post("/orders", (req, res) => {
  const { items, area } = req.body ?? {};
  const okItems = Array.isArray(items) && items.length > 0 && items.every((i) => typeof i === "string");
  if (!okItems || typeof area !== "string" || !area.trim()) {
    return res.status(400).json({ error: "Send items (a list of dishes) and area" });
  }
  const order = { id: nextId++, items, area, status: "preparing" };
  ORDERS[order.id] = order;
  res.status(201).json(order);
});

const port = Number(process.env.PORT || 3000);
app.listen(port, "0.0.0.0", () => console.log(`Dabba Express API on http://0.0.0.0:${port}`));
