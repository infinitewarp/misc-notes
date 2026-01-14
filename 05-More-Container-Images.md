# Container Image Deeper Dive

## Pull some images

```
podman pull registry.access.redhat.com/ubi10/ubi
podman pull registry.access.redhat.com/ubi10/ubi-minimal
podman pull alpine:latest

podman images
```

## Looking at a basic container image

Pull a small image, save it, and expand it:
```
mkdir -p /tmp/images/alpine && cd /tmp/images/alpine
podman pull alpine:latest
podman save alpine:latest -o /tmp/images/alpine.tar
tar -xf ../alpine.tar
```

Look inside:
```
ls -la
tree
```

The manifest tells the runtime which layers to stack and the config file.
Notice that your local image manifest may have different layer IDs than mine!
```
jq -C . manifest.json
```

The repositories tells you where you got the layers.
```
jq -C . repositories
```

The config (from the manifest) describes the build history, environment variables, what command run when starting the container, and more. These long IDs are sha256sum hashes.
```
jq -C . e8f9ca9f1870bc194d961e259fd1340c641bf188e0d02e58b86b86445a4bc128.json | less -R
```

## Digging into its layer(s)

Find the layer's ID.tar file from the manifest. Let's look inside it! It should look like a typical Linux root filesystem.

```
jq -C '.[] | .Layers' manifest.json

tar -tf 1869137e3b746de54b735253d5641cdc70b86dbab8a26b9aafcd5faaecc25a8f.tar | less
```

## Comparing with a bigger image with multiple layers

Remember that your local image manifest may have different layer IDs!

```
mkdir -p /tmp/images/discovery-server && cd /tmp/images/discovery-server
podman pull registry.redhat.io/discovery/discovery-server-rhel9:latest
podman save registry.redhat.io/discovery/discovery-server-rhel9:latest -o /tmp/images/discovery-server.tar

tar -xf ../discovery-server.tar

ls -la
```

Note that this image has two layers. The order of the layers is important: the runtime constructs the container's filesystem by writing each layer over the next in order.
```
jq -C . manifest.json

tar -tf 866a3cbc9ea47788d5f80d7c599f9b6852ec0a908ccb5b978f0910a703e4f8bd.tar | less
tar -tf 75b891a9bfaec7acd2ac6db38f8833efece9dfdc318f67332f2855e126694308.tar | less

```

Note that this image has a more complex config than alpine's.
```
jq -C . 8cb0d278d82289ddd5e1abedc02ae86ee457662110faa63e23b33de4cbc59915.json | less -R
```

## Creating an image the HARD way

Observe what a normal `alpine` container does.
```
podman run --rm -it alpine:latest
```

Note that I'm using `--rm` to make podman remove the container after it exits. If we do not remove it, the container data remains after it exists, and unless I want to look at its logs or dig through its files, it is rather useless to me.
```
podman run alpine:latest
podman ps -a
podman logs 5cee461794bb  # if interesting was output
podman inspect 5cee461794bb  # if I want to know more
podman start -a 5cee461794bb  # if I want to rerun it
podman rm 5cee461794bb  # clean it up
```

Let's put a file in the `alpine` image.
```
cd /tmp/images/alpine
echo 'Hello world!' > message.txt

# find the layer tar
jq -C . manifest.json

# append to the tar (might need to make writable first)
ls -la 1869137e3b746de54b735253d5641cdc70b86dbab8a26b9aafcd5faaecc25a8f.tar
chmod +w 1869137e3b746de54b735253d5641cdc70b86dbab8a26b9aafcd5faaecc25a8f.tar
tar -rf 1869137e3b746de54b735253d5641cdc70b86dbab8a26b9aafcd5faaecc25a8f.tar message.txt
chmod -w 1869137e3b746de54b735253d5641cdc70b86dbab8a26b9aafcd5faaecc25a8f.tar
```

Calculate and update the modified layer's sha256sum.
```
sha256sum 1869137e3b746de54b735253d5641cdc70b86dbab8a26b9aafcd5faaecc25a8f.tar
# remember this value for later
# af75acf3fdf6a0c5a3b9620a18ed282cb4f01b7a4b83655007eb015ecfdd00d0
```

Now, find its config.
```
# find the config
jq -C . manifest.json
```

Replace `"Cmd":["/bin/sh"]` with `"Cmd":["cat", "/message.txt"]`, and set the hash in the `diff_ids` array.
```
chmod +w e8f9ca9f1870bc194d961e259fd1340c641bf188e0d02e58b86b86445a4bc128.json
vim e8f9ca9f1870bc194d961e259fd1340c641bf188e0d02e58b86b86445a4bc128.json
chmod -w e8f9ca9f1870bc194d961e259fd1340c641bf188e0d02e58b86b86445a4bc128.json
```

Rename the config to its sha256sum hash:
```
sha256sum e8f9ca9f1870bc194d961e259fd1340c641bf188e0d02e58b86b86445a4bc128.json
# bd3fd085f16139414e4dabf5d35bd74cd5154ab2c4e6c27fb4e4cdfd240b58f5

mv e8f9ca9f1870bc194d961e259fd1340c641bf188e0d02e58b86b86445a4bc128.json bd3fd085f16139414e4dabf5d35bd74cd5154ab2c4e6c27fb4e4cdfd240b58f5.json
```

Update the manifest with the new config file name:
```
chmod +w manifest.json
vim manifest.json
chmod -w manifest.json
```

Create a new tarball with our modifications.
```
tar -cf custom-alpine.tar *
```

Remove old images, and add the modified image.
```
podman rmi --all
podman load -i custom-alpine.tar
```

Quick review from podman's perspective
```
podman images
podman inspect docker.io/library/alpine:latest | jq -C . | less -R
# look for "Cmd"
```

Run the modified image exactly like you ran the original!
```
podman run --rm -it alpine:latest
```

## Creating an image the *right* way

```
mkdir /tmp/images/new && cd /tmp/images/new
```

```
echo 'Hello world 2!' > message.txt
vim Containerfile
```

```Containerfile
FROM docker.io/library/alpine:latest
ADD ./message.txt /
CMD ["cat", "message.txt"]
```

Remove existing images, and build this one.
```
podman rmi --all
podman build -t custom-alpine .
```

Run it!
```
podman images
podman run --rm custom-alpine
```

## Next steps...?

Investigate what the registry has to say about its images?

```
skopeo inspect "docker://docker.io/library/alpine" | jq -C . | less -R
skopeo inspect "docker://registry.access.redhat.com/ubi9/ubi-minimal:latest" | jq -C . | less -R
```

Investigate multi-arch image manifests?

```
# check all manifests
skopeo inspect --raw docker://docker.io/library/alpine:latest | jq -C . | less -R
podman manifest inspect docker.io/library/alpine | jq -C . | less -R

# check for a specific cpu arch
skopeo inspect --override-arch arm64 docker://docker.io/library/alpine:latest
```

Creating a multi-stage image? Look at quipucords as an example.
