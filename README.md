# `side_projects`

This repository is a hodgepodge monorepo of small projects being 
undertaken by Peter Kaloyannis and Maria Navarro.

## Getting Started

This repository is built upon the popular [UV](https://github.com/astral-sh/uv) 
python package manager. We also recommend running these projects within a
linux environment (either WSL-2, VM, or native). For said environments, UV can
be installed with the following

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

UV is written in Rust, and the repository also might include instances of rust code. 
Rust is easily installed using the following commands.

```
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```

## Development

This repository uses `pre-commit` to run some simple checks before commiting code is 
possible. `pre-commit` is simple to setup using `uv` by running

```
uv tool install pre-commit
uvx pre-commit install
```

This will install `pre-commit` into the git commit system.

## Projects

- `feed_me` is an ultralightweight CLI task list system that abstracts away the decision making process.
