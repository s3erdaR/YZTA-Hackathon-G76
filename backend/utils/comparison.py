def compare_sentences_and_get_mistakes(expected: str, actual: str):
    expected = expected.strip().lower()
    actual = actual.strip().lower()

    mistakes = []
    for e_char, a_char in zip(expected, actual):
        if e_char != a_char and e_char.isalnum():
            mistakes.append(e_char)

    return list(set(mistakes))