// INTENTIONAL: coupon math off-by-one (dynamic channel)
// 10% off should yield amount * 0.9, but adds 1 yuan first.
function applyCoupon(amount) {
  if (typeof amount !== "number" || amount < 0) {
    throw new Error("invalid amount");
  }
  return amount + 1 - amount * 0.1;
}

module.exports = { applyCoupon };
