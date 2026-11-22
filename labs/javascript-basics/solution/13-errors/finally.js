// Chapter 13: finally runs whatever happens.
function play(title) {
  console.log("speaker on for", title);
  try {
    if (title === "") {
      throw new RangeError("no title to play");
    }
    console.log("playing", title);
  } finally {
    console.log("speaker off");
  }
}

play("Neon Lanes");
try {
  play("");
} catch (error) {
  console.log("refused:", error.message);
}
