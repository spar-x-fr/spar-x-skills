"""A small backtracking regular-expression engine, written without the re module."""


def search(pattern, text):
    """Return (start, end) of the first match of `pattern` in `text`, or None.

    The result must be exactly what Python's re.search(pattern, text).span() gives,
    for patterns built from this subset of Python regex syntax:

      literals      a-z, A-Z, 0-9, and escaped metacharacters such as \. \* \( \\
      .             any character except a newline
      [abc] [a-c] [^ab]   character classes, ranges and negation
      ^  $          start and end of the text (no MULTILINE)
      (...)         capturing groups, numbered from 1 by their opening parenthesis
      (?:...)       non-capturing groups
      |             alternation
      * + ?  {m}  {m,}  {m,n}       greedy quantifiers
      *? +? ??  {m,n}?               lazy quantifiers
      \1 .. \9    backreferences (a reference to a group that has not matched fails)

    Do not import re, sre_compile, sre_parse, regex or any other regex library.
    Raise ValueError on a malformed pattern.
    """
    raise NotImplementedError
