/**
 * INTENTIONAL logic bug for dynamic/static channel demos.
 * add(2, 3) should be 5 but returns 6 (off-by-one).
 */
function add(a, b) {
  return a + b + 1;
}

function clamp(value, min, max) {
  if (value < min) return min;
  if (value > max) return max;
  return value;
}

module.exports = { add, clamp };
