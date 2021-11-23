# Lispy Latex --- Insert lisp snippets into latex source code

## Usage

Use the decorator `@lisp` followed by a lisp snippet anywhere to
expand to its corresponding latex snippet. Once fully implement, one
should be able to write whole latex files from lisp, but I do not
recomment it. **NOTICE: THIS PROJECT IS FAR FROM FINISHED.**

## Examples

The following snippet
```latex
\documentclass[12pt]{article}
\begin{document}
The golden ratio is:
@lisp (begin! equation (= \phi (frac! (+ 1 (sqrt! 5)) 2)))
\end{document}
```

expands to
```latex
\documentclass[12pt]{article}
\begin{document}
The golden ratio is:
\begin{equation}
  \phi = \frac{1 + \sqrt{5}}{2}
\end{equation}
\end{document}
```

## Usage

```bash
Lispy Latex: Expands lisp snippets to latex
Usage: python lispytex [FILE]
Options:
-f [FILE]          Input to program
-o [FILE]          Redirect output to [FILE]
-h                 Help/usage page
```

## TODO:

- [_] Inplace replacement
