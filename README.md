# `side_projects`

This repository is a hodgepodge monorepo of small projects being 
undertaken by Peter Kaloyannis and Maria Fernanda Navarro Castillo.

## Getting Started

This repository is built upon the pupular [UV](https://github.com/astral-sh/uv) 
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

## Projects

- `feed_me` is an ultralightweight CLI task list system that abstracts away the decision making process.