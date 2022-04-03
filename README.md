# tools

Repository of useful tools that I developed and use on a day-to-day basis.

## python

In `python` directory are the tools written in python. Each will have its own subdirectory inside
`python/apps`. Subdirectory `python/apps/util` is for libraries and utilities that are not specific
of single app. All tests should be placed in `python/tests` tree, and this tree should reflect the
tree in `python/apps`.

To run Python unit tests:

```bash
PYTHONPATH=python python python/tests
```

## Tools

* [`keep_testing`](python/apps/keep_testing/README.md)
