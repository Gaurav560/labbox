// Chapter 6: two quiet bugs, found and fixed.

function totalLength(seconds) {
  let total = 0;
  for (let i = 0; i < seconds.length; i++) {
    total = total + seconds[i];
  }
  return total;
}

function canAdd(count, limit) {
  const room = limit - count;
  return room > 0;
}

if (require.main === module) {
  console.log(totalLength([200, 180, 240]));
  console.log(canAdd(10, 10));
}

module.exports = { totalLength, canAdd };
