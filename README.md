# Jarvis PKG

Jarvis-pkg is a system for installing and managing packages which have multiple installation
methods or nontrivial installation pipelines unsupported by spack. Jarvis-pkg supports
both building from source and installing from distro-specific binaries using the system's
package manager.

When installing a new package, jarvis-pkg will build all packages not already installed
on the system from source by default. This minimizes the assumption of root privileges
without discarding the software already on the system.

Users can register externally-built libraries or modulefiles to allow jarvis-pkg to take
full advantage of the software already installed on the system.

## Dependencies

* jarvis-cd

## Installation

This repo is installed as part of the Jarvis system.

## Usage

In order to use distro-specific package managers, you must specify your specific distro.
```
jpkg list-distros
jpkg set-distro [DISTRO_TYPE]
```

```
jpkg install package-name [--prefer-source] [--prefer-distro]
jpkg uninstall package-name
jpkg versions [pkg-name]
jpkg list [pkg-name or class-name]
jpkg find [pkg-name or class-name]
jpkg load [pkg-name]
```

Todo: jarvis-pkg installation pipeline
```
export JARVIS_PKG_ROOT=`pwd`
```