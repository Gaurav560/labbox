:::step{type=story title="A small problem"}
:::character{name="Priya" role="Founder"}
Tell the learner who needs what, and why it matters today.
:::

:::mission
Say in one line what they will build in this chapter.
:::
:::

:::step{type=concept title="One idea"}
Explain one idea in under 120 words. Show a short example:

```java
static int triple(int n) {
    return n * 3;
}
```
:::

:::step{type=predict title="Guess first"}
:::question
What does `triple(4)` give back?
:::
- [ ] `7`
- [x] `12`
- [ ] `43`
:::explain
`n * 3` multiplies, so `triple(4)` is `12`.
:::
:::

:::step{type=try title="Try it"}
```bash run
javac Twice.java && java Twice
```
:::

:::step{type=task task=twice title="Double a number"}
Make `twice(n)` in `Twice.java` return `n` times two. `twice(21)` returns `42`.
:::

:::step{type=recap}
- One takeaway.
- Another takeaway.
- A third takeaway.
:::
