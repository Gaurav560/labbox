// Chapter 17: tests for formatDuration. Run them with: node --test
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { formatDuration } = require("./duration.js");

test("a whole minute", () => {
  assert.equal(formatDuration(60), "1:00");
});

// TODO (task test_duration): more tests, so that any wrong change to formatDuration makes at least one fail.
