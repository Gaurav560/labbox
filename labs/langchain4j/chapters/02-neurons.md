:::step{type=story title="Will the 7:15 be late?"}
Every evening the station master at Pune decides whether to warn tomorrow morning's passengers that the 7:15 Ghat
Express will be late. She knows the signs from experience: heavy rain makes it slower, a holiday rush makes it
slower, track work on the ghat makes it much slower. She weighs them in her head and decides.

Chapter 1 learned one number from data, a threshold. Real decisions depend on several things at once, some more than
others. The building block that weighs several inputs and decides is an **artificial neuron**, and stacks of them are
what "deep learning" means. A large language model is, underneath, billions of these simple calculations.

:::mission
Build one neuron in Java, then train it on past mornings until it predicts, like the station master, which trains
will be late.
:::
:::

:::step{type=concept title="A neuron: weigh, add, decide"}
An artificial neuron is a very small function:

1. it takes some **inputs** (numbers), for example rain = 1, holiday = 0, track work = 1;
2. it multiplies each input by a **weight**, which says how much that input matters;
3. it adds them up, plus one more number, the **bias**, which shifts how easily it fires;
4. it **fires** (answers 1) if the total is above zero, and stays quiet (answers 0) otherwise.

```text
total = rain × w1 + holiday × w2 + trackWork × w3 + bias
late  = total > 0 ? 1 : 0
```

:::diagram{name="l4j-neuron"}
Three inputs flow into the neuron, each multiplied by its weight; the neuron adds them and the bias, and fires if the total is above zero.
:::

The inputs come from the world. The **weights and the bias are what the neuron learns**: they are its knowledge. Those
adjustable numbers have a general name you will meet everywhere: **parameters**. When people say a language model
"has 8 billion parameters", they mean 8 billion numbers like `w1`, learned in training.

The name comes from biology: a brain cell receives signals from others, and fires when the combined signal is strong
enough. The artificial version borrows only that idea; it is plain arithmetic.

**Check yourself:** with weights 0.5, 0.5 and a bias of -0.4, does the neuron fire for inputs 1 and 0? (0.5 + 0 - 0.4
= 0.1, above zero: yes, it fires.)
:::

:::step{type=history title="From a lab in Buffalo to billions of parameters"}
In **1943** Warren McCulloch and Walter Pitts described a mathematical model of a brain cell that adds its inputs and
fires past a threshold. In **1958** the psychologist **Frank Rosenblatt**, at the Cornell Aeronautical Laboratory in
Buffalo, New York, added the missing piece: a rule for **learning** the weights from examples. He called his neuron
the **perceptron**, and built it in hardware: the **Mark I Perceptron**, with a camera of 400 light sensors wired to
motors that turned knobs (the weights), learned to tell simple shapes apart.

:::photo{src="/lesson-images/langchain4j/mark-i-perceptron.webp" alt="The Mark I Perceptron in 1960: a camera on a tripod in front of tall cabinets of wiring, labelled S-unit monitor, association units and response panel" credit="John C. Hay and Albert E. Murray" license="Public domain" source="https://commons.wikimedia.org/wiki/File%3AMark_I_Perceptron%2C_Figure_2_of_operator%27s_manual.png"}
The Mark I Perceptron, from its 1960 operator's manual: the camera was its eye.
:::

:::before{title="One neuron is not enough"}
In **1969** Marvin Minsky and Seymour Papert published a book, *Perceptrons*, proving that a single neuron cannot learn
some very simple rules, for example "late if it rains **or** there is track work, **but not both**" (that rule is
called XOR). Funding for neural networks dried up for more than a decade.
:::

The answer was **layers**: neurons whose outputs feed other neurons can learn rules that one neuron cannot. In **1986**
David Rumelhart, Geoffrey Hinton and Ronald Williams showed how to train such networks with **backpropagation**, which
works out how much each weight in every layer contributed to a mistake. Networks with many layers became **deep
learning**. They needed two more things to shine, lots of data and fast hardware, and both arrived in the 2010s:
graphics cards, built for games, turned out to be ideal for multiplying millions of weights at once.

:::solved
**Learning, not programming.** A neural network is a long chain of the calculation you will write today. Its behaviour
is not written by anyone; it is in its weights, found by training. GPT-3 (2020) had 175 billion of them.
:::

:::timeline
- **1943** McCulloch and Pitts: a mathematical neuron.
- **1958** Rosenblatt's perceptron learns its own weights.
- **1969** *Perceptrons*: one neuron cannot learn XOR.
- **1986** Backpropagation trains networks with many layers.
- **2012** Deep networks on graphics cards win at recognising images.
- **2020** GPT-3: 175 billion parameters.
:::

:::funfact
In 1958 *The New York Times* reported that the Navy expected the perceptron to "be able to walk, talk, see, write,
reproduce itself and be conscious of its existence". It could tell a square from a circle.
:::
:::

:::step{type=example title="Worked example: weighing inputs" file="02-neurons/src/main/java/com/setu/Neuron.java" line="13-17"}
Here is the same weigh-and-add idea for a different decision, whether to open a second ticket window (only to read;
it is not in your project):

```java
// inputs: queue length in tens of people, minutes to the next train (in tens)
static boolean openSecondWindow(double queue, double minutes) {
    double total = queue * 0.8 + minutes * -0.3 - 1.0;  // weights 0.8, -0.3; bias -1.0
    return total > 0;
}
```

With 30 people in the queue (3.0) and 10 minutes to the train (1.0): 2.4 - 0.3 - 1.0 = 1.1, above zero, so open the
window. Notice the negative weight: the more time before the train, the less urgent. Weights can push either way.

Your `fire` does the same for **any number of inputs**: loop over them, add `inputs[i] * weights[i]` to a running total
that starts at the bias, then compare with zero.
:::

:::step{type=task task=neuron_fire title="Your turn: make the neuron fire" file="02-neurons/src/main/java/com/setu/Neuron.java" line="13-17"}
Finish `Neuron.fire(inputs, weights, bias)`: multiply each input by its weight, add them all and the bias, and return
`1` if the total is **greater than** zero, otherwise `0` (exactly zero does not fire).

Press **Check**.
:::

:::step{type=concept title="Training: nudge the weights towards the right answer"}
A neuron with the wrong weights makes wrong predictions. Rosenblatt's **perceptron rule** fixes them a little at a time,
using examples where you know the answer:

1. start with every weight, and the bias, at 0;
2. for one example, compute the neuron's guess with `fire`;
3. the **error** is `answer - guess`: 0 if it was right, +1 if it said "on time" for a late train, -1 the other way;
4. move each weight by `rate × error × input`, and the bias by `rate × error`;
5. do this for every example, and repeat the whole pass (an **epoch**) several times.

Read step 4 slowly, because it is the heart of all machine learning. When the guess is right, the error is 0 and
nothing changes. When the neuron wrongly said "on time" on a rainy morning, the rain weight grows, so next time rain
pushes the total up. An input that was 0 changes nothing, because it did not cause the mistake. The **learning rate**
(`rate`, here 0.1) is the size of each nudge: too big and the weights jump around, too small and training is slow.

:::trace{title='Training on one example: rain, no holiday, track work; the train was late'}
| step | weights | bias | total | guess | error | note |
|---|---|---|---|---|---|---|
| start | [0, 0, 0] | 0 | 0 | 0 | 1 | All zero: the total is 0, so it does not fire, but the train was late. |
| update | [0.1, 0, 0.1] | 0.1 | | | | Rain and track work were 1, so their weights grow by 0.1 × 1 × 1. Holiday was 0: unchanged. |
| again | [0.1, 0, 0.1] | 0.1 | 0.3 | 1 | 0 | Same example: 0.1 + 0.1 + 0.1 = 0.3, it fires. Right, so nothing changes. |
:::

Large language models are trained with a more powerful relative of this rule (backpropagation with gradient descent),
over trillions of words, on thousands of graphics cards for months. But every step is still: guess, measure the
error, nudge every weight a little in the direction that would have been less wrong.
:::

:::step{type=task task=train_neuron title="Your turn: train the neuron" file="02-neurons/src/main/java/com/setu/Neuron.java" line="19-24"}
Finish `Neuron.train(xs, ys, epochs, rate)` with the perceptron rule: start at zero; for each epoch, for each example,
compute the error and nudge every weight and the bias. Return `new Weights(w, bias)`.

```bash run
cd /workspace/02-neurons && mvn -q compile exec:java
```

Press **Check**.
:::

:::step{type=try title="The neuron learned the station master's rule"}
```text
$ mvn -q compile exec:java
weights [0.1, 0.2, 0.30000000000000004], bias -0.2
[0.0, 0.0, 0.0] -> predicted 0, actual 0
[1.0, 0.0, 0.0] -> predicted 0, actual 0
[0.0, 1.0, 0.0] -> predicted 0, actual 0
[0.0, 0.0, 1.0] -> predicted 1, actual 1
[1.0, 1.0, 0.0] -> predicted 1, actual 1
[1.0, 0.0, 1.0] -> predicted 1, actual 1
[0.0, 1.0, 1.0] -> predicted 1, actual 1
[1.0, 1.0, 1.0] -> predicted 1, actual 1
```

Look at the weights it found: track work (0.3) matters most, then the holiday (0.2), then rain (0.1), and the bias
(-0.2) means "on time unless the inputs add up to more than 0.2". From eight past mornings the neuron worked out that
track work alone makes the train late, while rain or a holiday alone does not, but any two together do. Nobody wrote
that rule.

The `0.30000000000000004` is not a bug in your code: computers store decimals in binary, and 0.1 added three times is
not exactly 0.3. Models live with tiny rounding everywhere; it does not change the decisions.
:::

:::step{type=try title="What one neuron cannot learn"}
Here is Minsky and Papert's problem, run with your `train` (only to read; it is not in your project): "late if it rains
or there is track work, but not both" (XOR), trained for 1000 epochs:

```text
[0.0, 0.0] -> predicted 1, actual 0   wrong
[1.0, 0.0] -> predicted 1, actual 1
[0.0, 1.0] -> predicted 0, actual 1   wrong
[1.0, 1.0] -> predicted 0, actual 0
```

After a thousand epochs it still gets two of the four cases wrong, and training longer never fixes it. It can only draw a single straight line
between "late" and "on time", and no straight line separates these four points. Two layers of neurons can, which is
exactly why networks are built in layers, and why the deep in deep learning means "many layers".
:::

:::step{type=predict title="Guess first"}
:::question
A trained neuron has weights rain 0.1, holiday 0.2, track work 0.3 and bias -0.2. Tomorrow has a holiday rush and
track work, but no rain. What does it predict?
:::
- [x] Late: 0.2 + 0.3 - 0.2 = 0.3, above zero
- [ ] On time: rain is 0
- [ ] It cannot say without retraining
:::explain
Once trained, a neuron just computes: weigh, add, compare. Training is slow; using the trained weights (called
**inference**) is fast. The same is true of a language model answering your question.
:::
:::

:::step{type=predict title="Quick check (1 of 2)"}
:::question
What does a model "learn" during training?
:::
- [ ] New lines of Java code
- [x] The values of its parameters: weights and biases
- [ ] A list of every example, to look up later
:::explain
The code (`fire`) never changes; training only changes the numbers it uses. A language model's knowledge, all of it,
is stored in its parameters.
:::
:::

:::step{type=predict title="Quick check (2 of 2)"}
:::question
Why are neural networks built from many layers?
:::
- [ ] To make them slower and more accurate
- [x] A single neuron can only separate cases with a straight line; layers can learn far more complex rules
- [ ] Each layer stores a different language
:::explain
Layers combine simple decisions into complex ones. A language model has dozens of layers, each turning the text into
a richer representation for the next.
:::
:::

:::step{type=deep-dive title="Go deeper: from one neuron to a transformer"}
**Smooth instead of a step.** Real networks replace "fire if above zero" with smooth functions (sigmoid, ReLU, GELU), so
a small change in a weight makes a small change in the output. That is what lets backpropagation work out how to nudge
millions of weights at once.

**Layers as matrices.** A layer of 1,000 neurons, each with 1,000 inputs, is one multiplication of a vector by a
1,000 by 1,000 matrix. Graphics cards do exactly that operation, billions of times a second, which is why AI runs on
them.

**What a parameter costs.** A model with 8 billion parameters, stored as 16-bit numbers, needs about 16 GB of memory
just to hold its weights, before it reads a single word. That is why the biggest models run in data centres, and why
"small" open models (chapter 24) are popular for laptops.
:::

:::step{type=recap}
You can now:

- explain an artificial neuron: inputs times weights, plus a bias, fire above zero;
- write `fire` and train it with Rosenblatt's perceptron rule;
- explain parameters, training, epochs, the learning rate and inference;
- say why one neuron cannot learn XOR and why networks have layers.

Next, chapter 3: from numbers to words. How computers learned to handle language, ending with a tiny language model
that predicts the next word.

:::photo{src="/lesson-images/langchain4j/l4j-02-notes.webp" alt="Handwritten notes about neurons: inputs times weights plus bias; fire if the total is above 0; weights and bias are parameters; training: guess, error, nudge; one neuron cannot learn XOR" ai="true"}
One page of notes for this chapter.
:::
:::
