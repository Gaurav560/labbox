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

// TODO (task get_order): GET /orders/:id answers the order as JSON, or 404 with {"error": "..."}.

// TODO (task create_order): POST /orders with {"items": [...], "area": "..."}.
//   Valid: items is a non-empty array of strings and area is a string.
//   Answer 201 with the new order ({id, items, area, status: "preparing"}), or 400 with {"error": "..."}.

const port = Number(process.env.PORT || 3000);
app.listen(port, "0.0.0.0", () => console.log(`Dabba Express API on http://0.0.0.0:${port}`));
