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

```python
def triple(n):
    return n * 3
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
python3 -c "from solution import double; print(double(21))"
```
:::

:::step{type=task task=double title="Double a number"}
Make `double(n)` in `solution.py` return `n` times two. `double(21)` returns `42`.
:::

:::step{type=recap}
- One takeaway.
- Another takeaway.
- A third takeaway.
:::
