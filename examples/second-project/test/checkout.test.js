const test = require("node:test");
const assert = require("node:assert/strict");
const { applyCoupon } = require("../src/checkout.js");

test("10% coupon on 100 yields 90", () => {
  // INTENTIONAL: will fail because of off-by-one in applyCoupon
  assert.equal(applyCoupon(100), 90);
});

test("rejects negative amount", () => {
  assert.throws(() => applyCoupon(-1));
});
