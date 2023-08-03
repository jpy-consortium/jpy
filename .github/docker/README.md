# docker buildx bake

This is an alternative way to build the jpy Linux wheels.
It is mainly used as a means to produce arm64 wheels via QEMU cross-compiling since GHA does not have a native Linux arm64 runner.

That said, it can be useful locally too; either to produce native or arm64 Linux wheels.

```bash
docker buildx bake \
  --file .github/docker/docker-bake.hcl \
  --set "*.output=type=local,dest=/tmp/dist"
```

```bash
docker buildx bake \
  --file .github/docker/docker-bake.hcl \
  --set "*.output=type=local,dest=/tmp/dist" \
  --set "*.platform=linux/arm64/v8" 
```
