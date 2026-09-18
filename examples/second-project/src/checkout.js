// 10% off yields amount * 0.9
function applyCoupon(amount) {
  if (typeof amount !== "number" || amount < 0) {
    throw new Error("invalid amount");
  }
  return amount * 0.9;
}

module.exports = { applyCoupon };
