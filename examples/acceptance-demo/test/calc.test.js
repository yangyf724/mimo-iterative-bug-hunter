const test = require("node:test");
const assert = require("node:assert/strict");
const { add, clamp } = require("../src/calc");

test("add returns sum of two numbers", () => {
  assert.equal(add(2, 3), 5);
});

test("clamp bounds value", () => {
  assert.equal(clamp(10, 0, 5), 5);
  assert.equal(clamp(-1, 0, 5), 0);
  assert.equal(clamp(3, 0, 5), 3);
});
