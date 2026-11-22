// Chapter 10: is the number 1 the same key as the text "1"?
const box = {};
box[1] = "the number one";
box["1"] = "the text one";
console.log(box, Object.keys(box));

const map = new Map();
map.set(1, "the number one");
map.set("1", "the text one");
console.log(map.size, map.get(1), map.get("1"));
