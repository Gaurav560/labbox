// Chapter 6: a crash two functions deep.
function longestTitle(titles) {
  let best = titles[0];
  for (const title of titles) {
    if (title.length > best.length) {
      best = title;
    }
  }
  return best;
}

function headline(name, titles) {
  return name + ": " + longestTitle(titles).toUpperCase();
}

console.log(headline("Morning", ["Neon Lanes", "Monsoon Drive"]));
console.log(headline("Evening", []));
