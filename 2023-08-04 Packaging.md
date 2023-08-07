# Packaging

### Or: everything looks like a TAR file if you stare long enough

## Overview

Some ways we package, distribute, and install software include:

* tar files (or `.tar.gz` or `.tgz`) ([wikipedia](https://en.wikipedia.org/wiki/Tar_(computing)))
	* simple file archives
	* a.k.a. "tarball"
* RPM files (originally Red Hat Package Manager) ([wikpedia](https://en.wikipedia.org/wiki/RPM_Package_Manager))
	* originally created by Marc Ewing, Red Hat founder
* container images ([specification](https://github.com/opencontainers/image-spec/blob/main/spec.md))
	* _exclusively_ used by container engines like Docker and podman
* AppImage, Snap, FlatPak
	* typically for distributing desktop GUI apps
	* basically an executable iso/archive
	* (Let's skip this one for now…)

## What's the difference? Why X instead of Y?

### tar file

* originally used for magnetic tape drive transfer and storage (`t`ape `ar`chives)
	![](https://learnlearn.uk/igcseict/wp-content/uploads/sites/3/2016/08/tape-drive.jpg)
* contains a sequence of file objects, one after the next
* each file object has its own header with metadata
	* including but not limited to: file size, modification date, owner, group, mode
* contains each file's data in a _raw uncompressed_ stream
* is just a "dumb" archive
	* does not have outside requirements or dependencies
* can be created and expanded virtually anywhere, platform independent

### RPM file

* is like a tar file _on steroids_ 💪
* contains a cryptographic signature of the author so you can verify authenticity
* includes various metadata including the name, version, intended CPU architecture, and more
* include a list of _other_ RPM dependencies (and their versions) that must be installed first
* contains many files _usually_ in a compressed format ([cpio](https://en.wikipedia.org/wiki/Cpio) file archive, then gzip compressed)
* requires writing a `spec` file to build the `rpm` file
	* https://rpm-software-management.github.io/rpm/manual/spec.html
	* https://rpm-packaging-guide.github.io/#hello-world
	* http://ftp.rpm.org/max-rpm/p5206.html
* once installed, is tracked by your OS's package manager, which you can then query
	* https://linux.die.net/man/8/rpm
	* `rpm -q python3.11`
	* `rpm -q --whatprovides /usr/bin/python3.11`
	* `rpm -qlivP python3.11`
* _generally_ requires a Red Hat-like OS (rhel, fedora, centos, ubi, etc)
	* you can _technically_ use rpm files on other Linux distros, but it's probably more trouble than it's worth because other distros have their own packaging tools
		* debian (and ubuntu) has `apt` and `dpkg` with `deb` files
		* arch has `pacman` and `makepkg` with `pkg` files (often `pkg.tar.zst`)
* is what `dnf` (formerly `yum`) downloads and installs being the scenes

### Container Image

* is also like a tar file on steroids, _but_ you rarely interact with any image files directly 🙈
* is generally _not_ downloaded manually or shared as individual files
* is usually `pull`ed from a registry online (like [hub.docker.com](https://hub.docker.com) or [GHCR](http://ghcr.io/) or [quay.io](https://quay.io))
	* which transfers and stores the [manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md) and [filesystem data](https://github.com/opencontainers/image-spec/blob/main/layer.md) automatically
	* see also: [OCI specification](https://github.com/opencontainers/distribution-spec/blob/main/spec.md#pull)
* is built using layers so that you can reuse other images without including their entire filesystem in your image
* is stored in expanded layers at `/var/lib/docker/`
	* note that everything in this path is owned by `root`
	* for podman, check
		* `/var/lib/containers/storage`
		* `$HOME/.local/share/containers/storage`
* can be exported and imported as tar files!
	* `docker save 22a1fc85032a -o ~/Desktop/22a1fc85032a.tar`
	* `docker image import ~/Desktop/22a1fc85032a.tar`
* serves as a **template** for the engine to _create_ a container's filesystem
	* `docker inspect CONTAINERID` to find the "merged" path

## How do we build container images?

### Dockerfile (or Containerfile)

- `Dockerfile` is overwhelmingly what people use because Docker popularized it.
- `Containerfile` is basically the same, minus the Docker trademark ([man page](https://github.com/containers/common/blob/main/docs/Containerfile.5.md))
- Usually starts with the name of another image to use as its base filesystem.
	- e.g. `FROM fedora:latest`
- Includes a list of commands to run programs and add files to build the filesystem.
- The container engine is responsible for building an image from the `Dockerfile`.
	-  `docker build` steps through the `Dockerfile` to create the image.
- Each `RUN`, `COPY`, and `ADD` command in the `Dockerfile` will produce a new _layer_.
	- A layer is a part of the image that is basically a saved "diff" of the filesystem.
	- This is why it's common practice to chain some commands together in a single `RUN` statement. If you need to install something just to run a command but don't need it afterwards, you may `install command && command && uninstall command` so that the resulting layer doesn't waste storage on keeping the command installed.
		- For example, [link](https://github.com/quipucords/quipucords/blob/main/Dockerfile#L19-L34)
- Another technique for minimizing wasted disk use is [multi-stage](https://docs.docker.com/build/building/multi-stage/) builds.
	- Each `FROM` line in the `Dockerfile` indicates a new stage.
	- Each stage's layers are stored separately during the build process.
	- Only the layers from the _last_ stage are included in the final image.
	- We use a multi-stage build when building downstream ([link](https://pkgs.devel.redhat.com/cgit/containers/discovery-server/tree/Dockerfile?h=discovery-1.3-rhel-9))