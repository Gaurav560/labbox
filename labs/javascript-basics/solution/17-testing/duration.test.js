// Chapter 17: tests for formatDuration. Run them with: node --test
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { formatDuration } = require("./duration.js");

test("a whole minute", () => {
  assert.equal(formatDuration(60), "1:00");
});

test("seconds below ten get a leading zero", () => {
  assert.equal(formatDuration(245), "4:05");
  assert.equal(formatDuration(5), "0:05");
});

test("an hour or more shows hours, with two-digit minutes", () => {
  assert.equal(formatDuration(3600), "1:00:00");
  assert.equal(formatDuration(3725), "1:02:05");
});

test("just under an hour stays in minutes", () => {
  assert.equal(formatDuration(3599), "59:59");
});

test("negative seconds are refused", () => {
  assert.throws(() => formatDuration(-1), RangeError);
});
