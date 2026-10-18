#!/usr/bin/env python3
"""Re-extract the GRADED FalkorDB module from the pinned container image.

Why this exists: the graded artefact is the falkordb/falkordb container, and the
module inside it reports ver 42201 (v4.22.1). The embedded falkordblite package is
v4.18.3, two majors apart, so it is NOT a substitute. This script downloads the
image layers named by the pinned manifest digest and extracts:
  - the FalkorDB module      (var/lib/falkordb/bin/falkordb.so)
  - the redis-server the image ships (usr/local/bin/redis-server)

Reads only public registry endpoints, with the anonymous pull token. No docker
daemon needed, which matters because no container runtime is installed on this host.

Writes .falkorimg/. Then run scripts/start_module.sh.
"""
import hashlib
import json
import os
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, ".falkorimg")
DIGEST = "sha256:b0bdcac2cbaff989e77cb0610439b7a9289e86de033ccbbd4368b66fb680ae7a"
REPO = "falkordb/falkordb"
ACCEPT_LIST = "application/vnd.docker.distribution.manifest.list.v2+json"
ACCEPT_MAN = "application/vnd.docker.distribution.manifest.v2+json"


def curl_json(url, token=None, accept=None):
    cmd = ["curl", "-sSL", "--max-time", "60"]
    if token:
        cmd += ["-H", "Authorization: Bearer " + token]
    if accept:
        cmd += ["-H", "Accept: " + accept]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("curl failed for %s: %s" % (url, r.stderr[:200]))
    try:
        return json.loads(r.stdout)
    except Exception as e:
        raise SystemExit("not JSON from %s: %s | head=%r" % (url, e, r.stdout[:200]))


def curl_file(url, dest, token=None):
    cmd = ["curl", "-sSL", "--max-time", "900", "-o", dest,
           "-w", "%{http_code} %{size_download}"]
    if token:
        cmd += ["-H", "Authorization: Bearer " + token]
    cmd.append(url)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("curl failed for %s: %s" % (url, r.stderr[:200]))
    code, size = r.stdout.split()
    if code != "200":
        raise SystemExit("HTTP %s for %s" % (code, url))
    return int(size)


def main():
    os.makedirs(OUT, exist_ok=True)
    tok = curl_json("https://auth.docker.io/token?service=registry.docker.io"
                    "&scope=repository:%s:pull" % REPO)["token"]
    print("got anonymous pull token (len %d)" % len(tok))

    idx = curl_json("https://registry-1.docker.io/v2/%s/manifests/%s" % (REPO, DIGEST),
                    token=tok, accept=ACCEPT_LIST)
    if "manifests" not in idx:
        print("no manifest list, body keys: %s" % list(idx.keys())[:8])
        raise SystemExit("FAIL: the pinned digest is not a manifest list")
    amd = [m for m in idx["manifests"] if (m.get("platform") or {}).get("architecture") == "amd64"]
    if not amd:
        raise SystemExit("FAIL: no amd64 manifest")
    man_digest = amd[0]["digest"]
    print("amd64 manifest digest: %s" % man_digest)

    man = curl_json("https://registry-1.docker.io/v2/%s/manifests/%s" % (REPO, man_digest),
                    token=tok, accept=ACCEPT_MAN)
    layers = man["layers"]
    print("layers: %d" % len(layers))

    got_module = got_redis = False
    for i, l in enumerate(layers):
        dest = os.path.join(OUT, "layer_%02d.tar.gz" % i)
        if not os.path.exists(dest):
            size = curl_file("https://registry-1.docker.io/v2/%s/blobs/%s" % (REPO, l["digest"]),
                             dest, token=tok)
        else:
            size = os.path.getsize(dest)
        h = hashlib.sha256()
        with open(dest, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        ok = ("sha256:" + h.hexdigest()) == l["digest"]
        print("  layer %02d %9d bytes digest_ok=%s" % (i, size, ok), flush=True)
        if not ok:
            raise SystemExit("FAIL: layer %d digest mismatch" % i)
        with tarfile.open(dest, "r:gz") as tf:
            names = tf.getnames()
            if any(n.endswith("var/lib/falkordb/bin/falkordb.so") for n in names):
                tf.extractall(os.path.join(OUT, "x%02d" % i))
                got_module = True
                print("     contains falkordb.so", flush=True)
            if any(n.endswith("usr/local/bin/redis-server") for n in names):
                tf.extractall(os.path.join(OUT, "x%02d" % i))
                got_redis = True
                print("     contains redis-server", flush=True)

    print("module=%s redis=%s" % (got_module, got_redis))
    if not (got_module and got_redis):
        raise SystemExit("FAIL: a required artefact is missing")
    print("OK: now run scripts/start_module.sh")


if __name__ == "__main__":
    main()
