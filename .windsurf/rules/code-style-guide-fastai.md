---
trigger: model_decision
---

### Keep it concise

- Keep the code compact, because “ _brevity facilitates reasoning_ ”
- Take advantace of the following Python possibilities to keep the code compact:
    * List, dictionary, generator, and set comprehensions
    * Lambda functions
    * Python 3.6 interpolated format strings
    * Numpy array-based programming.
- Aim to keep all the key ideas for one semantic concept below 60 lines of code.


### Naming conventions

* Follow standard Python casing guidelines (CamelCase classes, under_score for most everything else).
* In general, aim for shorter names for commonly used things, but don't waste short sequences on less common constructs.
* A fairly complete list of abbreviations is given `./aicontext/abbreviations.md
* Use `o` for an object in a comprehension, `i` for an index, and `k` and `v` for a key and value in a dictionary comprehension.
* Use `x` for a tensor input to an algorithm (e.g. layer, transform, etc), unless interoperating with a library where this isn’t the expected behavior (e.g. if writing a pytorch loss function, use `input` and `target` as is standard for that library).
* Take a look at the naming conventions in the part of code you’re working on, and try to stick with them.
### Layout

* A line of code should not be larger than 160 characters.
* One line of code should implement one complete idea, where possible
* Generally therefore an `if` part and its 1-line statement should be on one line, using `:` to separate
* Using the ternary operator `x = y if a else b` can help with this guideline
* If a 1-line function body comfortably fits on the same line as the `def` section, feel free to put them together with `:`
* If you’ve got a bunch of 1-line functions doing similar things, they don’t need a blank line between them

```python
def det_lighting(b, c): return lambda x: lighting(x, b, c)
def det_rotate(deg): return lambda x: rotate_cv(x, deg)
def det_zoom(zoom): return lambda x: zoom_cv(x, zoom)
```

* Aim to align statement parts that are conceptually similar. It allows the reader to quickly see how they’re different. E.g. in this code it’s immediately clear that the two parts call the same code with different parameter orders.

```python
if self.store.stretch_dir==0: x = stretch_cv(x, self.store.stretch, 0)
else:                         x = stretch_cv(x, 0, self.store.stretch)
```
* Put all your class member initializers together using destructuring assignment. When doing so, use no spaces after the commas, but spaces around the equals sign, so that it’s obvious where the LHS and RHS are.

```python
self.sz,self.denorm,self.norm,self.sz_y = sz,denorm,normalizer,sz_y
```
* Avoid using vertical space when possible, since vertical space means you can’t see everything at a glance. For instance, prefer importing multiple modules on one line.

```python
import PIL, os, numpy as np, math, collections, threading
```

* Indent with 4 spaces
* When it comes to adding spaces around operators, try to follow notational conventions such that your code looks similar to domain specific notation. E.g. if using pathlib, don’t add spaces around `/` since that’s not how we write paths in a shell. In an equation, use spacing to lay out the separate parts of an equation so it’s as similar to regular math layout as you can.
* Avoid trailing whitespace

### Algorithms

  * Try to ensure that your implementation of an algorithm is at least as fast, accurate, and concise as other versions that exist (if they do), and use a profiler to check for hotspots and optimize them as appropriate (if the code takes more than a second to run in practice).
  * Try to ensure that your algorithm scales nicely; specifically, it should work in 16GB RAM on arbitrarily large datasets. That will generally mean using lazy data structures such as generators, and not pulling everything in to a list.
  * Use numpy/pytorch broadcasting, not loops, where possible.
  * Use numpy/pytorch advanced indexing, not specialized indexing methods, where possible.

### Other stuff

  * Avoid comments unless they are necessary to tell the reader _why_ you’re doing something. To tell them _how_ you’re doing it, use symbol names and clear expository code.
  * If you’re implementing a paper or following some other external document, include a link to it in your code.
  * If you’re using nearly all the stuff provided by a module, just `import *`. There’s no need to list all the things you are importing separately! To avoid exporting things which are really meant for internal use, define `__all__`. currently following the `__all__` guideline, and welcome PRs to fix this.)
  * Keep your PRs small, and for anything controversial or tricky discuss it on the forums first.

### Documentation

  * Documentation largely goes in the notebooks in `docs_src`, which is used to create the HTML docs
  * In the code, add a one-line docstring which includes back-quoted references to the main params by name
  * The Python `re` module is a good role model for the documentation style we’re looking for.