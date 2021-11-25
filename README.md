# Lispy LaTeX --- Expands lisp snippets to LaTeX

## Usage

Use the decorator `@lisp` followed by a lisp snippet anywhere to
expand to its corresponding LaTeX snippet. Once fully implement, one
should be able to write whole LaTeX files from lisp, but I do not
recommend it. **NOTICE: THIS PROJECT IS FAR FROM FINISHED.**

Most of LaTeX's function can be used followed by a bang and a number
of arguments, e.g `(frac! 1 2)`. Some operations have been given a
name: e.g:`sub` is short for subscript (the operator `_` can also be
used). These can change at any time, so using the default names
followed by bang or, in the case of binary operators, simply using the
operator itself should give the desired output.

## Examples

The following snippet
```latex
\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{physics}
\begin{document}
The geometric series is
@lisp
(begin! equation
	(let ((lhs (plus 1 r (up r 2) (up r 3) (up r 4) \ldots ))
              (rhs (frac! 1 (minus 1 r))))
	  (eq lhs (plus rhs))))
for @lisp (abs! (< x 1)).
\end{document}
```

expands to
```latex
\documentclass[12pt]{article}
\usepackage{amsmath}
\usepackage{physics}
\begin{document}
The geometric series is
\begin{equation}
  1 + r + r^{2} + r^{3} + r^{4} + \ldots = \frac{1}{1 - r}
\end{equation}
for $\abs{x < 1}$.
\end{document}
```

## Usage

```bash
Lispy LaTeX: Expands lisp snippets to LaTeX
Usage: python lispytex [OPTIONS]
Options:
-f [FILE]          Input to program
-o [FILE]          Redirect output to [FILE]
-h                 Help/usage page
```

## TODO:

- [ ] Inplace replacement
