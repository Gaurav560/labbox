import math

import r


def test_softmax_temperature():
    def check():
        from attention import softmax
        got = softmax([2.0, 1.0, 0.0])
        want = [math.exp(2) / (math.exp(2) + math.exp(1) + 1), math.exp(1) / (math.exp(2) + math.exp(1) + 1), 1 / (math.exp(2) + math.exp(1) + 1)]
        if len(got) != 3 or any(abs(g - w) > 1e-9 for g, w in zip(got, want)):
            return r.failed("softmax_temperature", "Take math.exp of each score and divide each by their sum.", [round(w, 3) for w in want], got)
        cold, hot = softmax([2.0, 1.0], 0.5), softmax([2.0, 1.0], 2.0)
        if not cold[0] > softmax([2.0, 1.0])[0] > hot[0]:
            return r.failed("softmax_temperature", "Divide every score by the temperature before math.exp: a low temperature should make the top score win more.")
        if abs(sum(softmax([1000.0, 999.0])) - 1) > 1e-9:
            return r.failed("softmax_temperature", "Large scores overflow math.exp. Subtract the largest score from every score first; the result is the same.")
        r.passed("softmax_temperature", "Low temperature sharpens the choice, high temperature flattens it: the temperature knob of chapter 8.")
    r.task("softmax_temperature", check)


def test_attention_weights():
    def check():
        from attention import attention
        got = attention([1.0, 0.0], [[1.0, 0.0], [0.0, 1.0]])
        a = math.exp(1 / math.sqrt(2))
        want = [a / (a + 1), 1 / (a + 1)]
        if any(abs(g - w) > 1e-9 for g, w in zip(got, want)) or len(got) != 2:
            return r.failed("attention_weights", "Score each key by its dot product with the query divided by math.sqrt(len(query)), then softmax the scores.",
                            [round(w, 4) for w in want], got)
        r.passed("attention_weights", "Each word decides how much to look at every other word: the heart of a transformer, in five lines.")
    r.task("attention_weights", check)
