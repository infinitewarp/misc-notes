# RPMs deeper dive

## Getting RPMs

Download RPMs using `dnf`.

```sh
rm -rf ~/rpms && mkdir ~/rpms

# download a single RPM
dnf download --downloaddir ~/rpms tree

# --resolve also get its required dependencies
# --alldeps gets ALL dependencies, even ones already installed
dnf download --resolve --alldeps --downloaddir ~/rpms tree
```

Want the source RPMs too?

```sh
sudo dnf groupinstall "Development Tools"
# can undo this with like:
# sudo dnf groupremove "Development Tools" && sudo dnf autoremove && sudo dnf clean all

rm -rf ~/srpms && mkdir ~/srpms

# same as before, but add --source
dnf download --source --downloaddir ~/srpm tree

# optional --resolve --alldeps work too
dnf download --source --resolve --alldeps --downloaddir ~/srpms tree
```

Downloading directly from copr.

* find a recent build on https://github.com/quipucords/quipucordsctl
* e.g. https://download.copr.fedorainfracloud.org/results/@quipucords/quipucordsctl-latest/rhel-10-aarch64/10116649-quipucordsctl/

```sh
rm -rf ~/rpms && mkdir ~/rpms && cd ~/rpms
wget https://download.copr.fedorainfracloud.org/results/@quipucords/quipucordsctl-latest/rhel-10-aarch64/10116649-quipucordsctl/quipucordsctl-2.4.2-1.20260211145643890560.main.27.ga3ba8be.el10.noarch.rpm

```

## Querying RPM files

What does this RPM file contain?

```sh
# -q/--query = query
# -i/--info = info
# -p/--package = query this file, not the installed RPM database
rpm -qip ~/rpms/tree*rpm

# -l/--list = list contents
rpm -qlp ~/rpms/tree*.rpm

# --scripts = show included install/uninstall scripts
rpm -q --scripts -p ~/rpms/bash-*.rpm

# check `man rpm` section `PACKAGE QUERY OPTIONS` for more
```

What kind of metadata does it define?

```sh
# --queryformat = custom output format
rpm -qp --queryformat "[%{NAME}: %{SUMMARY}\n]" ~/rpms/tree*rpm

# get a list of all possible metadata tags
rpm --querytags

# `rpm -q` doesn't have an "all tags" option,
# but we can *iterate* to dump them all.
for tag in $(rpm --querytags); do
    value=$(rpm -qp --queryformat "%{$tag}" ~/rpms/tree*rpm 2>/dev/null)
    if [[ -n "$value" && "$value" != "(none)" ]]; then
        printf "%-30s : %s\n" "$tag" "$value"
    fi
done
```

Note that **_source_** RPMs are different and don't show full paths in the `-l`/`--list` query:

```sh
rpm -qlp ~/srpms/tree*.src.rpm
```

Let's install to see what happens.

```sh
rpm -ivh ~/srpms/tree*.src.rpm
```

Where did they go?

```sh
ls -la ~/rpmbuild/
tree ~/rpmbuild/
```

`~/rpmbuild/` is the standard location for the RPMs build environment. Installing a source RPM puts its files there, assuming you intend to build. For more information, see:

```sh
sudo dnf install rpmdevtools
vim $(which rpmdev-setuptree)
```

## Query the RPM Database

```sh
# query installed package by name
rpm -q tree

# same options as before
rpm -qli tree

# -a/--all = all installed packages
rpm -qa

# --last = include install date, latest at top
rpm -qa --last | head
rpm -qa --last | tail
```

## A closer look at an RPM file

How do programs like `rpm` and `dnf` know if a file is actually an RPM?

Check the magic bytes!

```sh
file ~/rpms/tree*rpm
# see also `man file`

less /usr/share/misc/magic # search for RPM
# 0xedabeedb

hexdump -C -n 16 ~/rpms/tree*rpm
# 00000000  ed ab ee db
```

Let's extract the contents of a binary RPM without installing.

```sh
# RPMs contain a compressed CPIO archive
rpm2cpio ~/rpms/tree*rpm > ~/rpms/tree.cpio
cpio -itv < ~/rpms/tree.cpio

# let's unpack it into a local directory
rm -rf ~/rpmfakeroot && mkdir ~/rpmfakeroot && cd ~/rpmfakeroot
cpio -idmv < ~/rpms/tree.cpio

tree -a .

# compare with what the actual install RPM did
rpm -ql tree
```

## Checking signatures

What is a signed RPM? It's an RPM that includes a cryptographic signature to verify the contents of the RPM have not been tampered with since it was created.

Cryptographic signatures use public-private key cryptography. Packages are signed using the author's private key, and anyone can verify using the author's public key.

Signatures are added AFTER an RPM is built. Only the RPM headers are signed, not the full binary data, but that's good enough because the headers include metadata and checksums of the binary data.

Checking RPM package signature

```sh
rpm --checksig ~/rpms/tree*rpm

# --checksig shorthand is -K
rpm -K ~/rpms/tree*rpm

# add -v or --verbose for details
# look for "RSA/SHA256 Signature"
rpm -K ~/rpms/tree*rpm
```

## Tampering with an RPM file

```sh

grep "Red Hat" ~/rpms/tree*rpm

cp ~/rpms/tree*rpm ~/rpms/tampered-tree*rpm
sed -i 's/Red Hat/Bad Hat/g' ~/rpms/tampered-tree*rpm

rpm -Kv ~/rpms/tampered-tree*rpm
```

## Replacing the signature

Remove the old signature

```sh
rpmsign --delsign ~/rpms/tree*rpm

# verify no more "RSA/SHA256 Signature"
rpm -Kv ~/rpms/tree*rpm
```

Generate keys for yourself

```sh
# generate a new key pair for yourself
gpg --full-generate-key

# export them if you wish
gpg --export -a "Your Name" > publickey.asc
# gpg --export-secret-key -a "Your Name" > privatekey.asc
# and someone else can import your public key
gpg --import publickey.asc
```

Sign the RPM using your private key

```sh
rpmsign --addsign --key-id="Your Name" ~/rpms/tree*rpm

# verify "RSA/SHA256 Signature"
rpm -Kv ~/rpms/tree*rpm
```

Note the `NOKEY` in the output! This means that the key used is not trusted by the system RPM keyring. So, let's import our new public key.

```sh
sudo rpm --import publickey.asc

# verify "OK" not "NOKEY"
rpm -Kv ~/rpms/tree*rpm
```

Clean up these keys before we dig into more RPM stuff

Before removing keys, copy the key ID shown in the last `rpm -Kv`.

```sh
# remove your generated keys
gpg --list-secret-keys
gpg --delete-secret-key ID
gpg --list-keys
gpg --delete-key ID

# find the keys trusted by RPM
ls /etc/pki/rpm-gpg/
rpm -qa gpg-pubkey*

# erase the one matching your key ID
sudo rpm --erase gpg-pubkey-KEYID
```
