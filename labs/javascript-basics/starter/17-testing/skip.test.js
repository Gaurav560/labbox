// Chapter 17: tests for the Skip button. Run them with: node --test
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { nextIndex } = require("./skip.js");

test("skip moves to the next song", () => {
  assert.equal(nextIndex(0, 3), 1);
});

test("after the last song, back to the first", () => {
  assert.equal(nextIndex(2, 3), 0, "the playlist should wrap around");
});
