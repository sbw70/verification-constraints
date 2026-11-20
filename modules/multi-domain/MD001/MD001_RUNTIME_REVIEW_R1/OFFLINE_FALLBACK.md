# Offline fallback if exact49 is required or a host probe fails

System packages do not meet the literal49 pin. They are source/API candidates only.
If the operator retains exact49 as a mandatory runtime criterion, or any host probe
fails, stop the system-runtime path and prepare a target-matched offline install.
No files have been downloaded or installed for this fallback.

1. Retain failure report and collect read-only host facts: /usr/bin/python3 version,
   implementation/cache tag, sysconfig platform/SOABI, uname -m, dpkg architecture,
   distro version and libc version. Pi3B+ hardware does not establish whether its OS
   is32-bit armhf or64-bit arm64. Do not assume a Windows or x86 wheel can run there.
2. On a trusted connected matching Linux preparation environment for each target
   architecture/Python, use pip download --only-binary=:all: --dest wheelhouse
   cryptography==49.0.0. Collect its complete resolved dependency set including
   platform-specific cffi/pycparser where required. Explicit cross-target download
   requires correct --platform, --python-version, --implementation and --abi tags;
   those values cannot be populated until the actual host architecture is recorded.
3. Select one exact compatible wheel for every dependency, pin every version and
   SHA256 in a new separate requirements49.lock, record origin URLs, tool version,
   platform tags and hashes. Preserve the original requirements.txt and bundle.
   Test that exact wheel set in an equivalent clean offline Linux environment before
   transfer. Do not fall back automatically to source builds on Pi.
4. If venv module is present but ensurepip alone is unavailable, a NEW sibling venv
   can be created with /usr/bin/python3 -m venv --without-pip NEW_ENV. Do not reuse
   or delete the partial .venv. Supply a separately hashed trusted pip wheel or
   pip zipapp; test the bootstrap on the matching preparation environment first.
   A pip wheel can be expanded using standard-library zipfile into a bootstrap
   directory and run via NEW_ENV/bin/python -B -s BOOTSTRAP/pip --isolated ... .
   The pip zipapp is another documented alternative but its current documentation
   calls its status experimental; do not treat it as a tested default here.
5. Proposed offline installer shape after separate install approval and staging:

```sh
# NEW_ENV, BOOTSTRAP and OFFLINE_MEDIA are reviewed absolute paths, not literals.
NEW_ENV/bin/python -B -s BOOTSTRAP/pip --isolated install --no-index --only-binary=:all: --require-hashes --find-links OFFLINE_MEDIA/wheelhouse -r OFFLINE_MEDIA/requirements49.lock
NEW_ENV/bin/python -B -s -c 'import sys, cryptography; print(sys.executable, cryptography.__version__, cryptography.__file__)'
```

   This writes only the new environment; no sudo, --user, --break-system-packages,
   DNS/network change or system Python package replacement. `--no-index` plus a
   reviewed local requirements lock (no remote URLs) and wheelhouse avoids host
   repository retrieval. Bootstrap must also be staged; ensurepip is not invoked.
6. If even venv --without-pip cannot work, separately stage matching distro venv
   packages plus their required closure on verified offline media. Simulate package
   changes first and require operator approval before installation. Do not run an
   automatic dependency repair that attempts online retrieval.
7. If no binary wheel exists for the Pi OS ABI, build in an equivalent trusted
   preparation environment with the documented compiler/Rust/OpenSSL/libffi/Python
   dependencies, produce a wheel, and test it offline. This is additional build work,
   not a claim the available packages already satisfy49.
8. Repeat full host runtime checks under the explicitly selected new49 interpreter,
   adjusting the probe profile policy in a new reviewed revision, not editing the
   frozen app. Existing dell/hp/pi profiles intentionally expect distro packages and
   will fail on a49 venv. Do not use desktop mode to claim Linux profile approval.
   Repeat non-scored service/HTTP preflight before separate scored-test authorization.

Primary references:
- https://pip.pypa.io/en/stable/cli/pip_download/
- https://pip.pypa.io/en/stable/installation/
- https://docs.python.org/3.12/library/venv.html

Exact wheel filenames, hashes, bootstrap artifact version and distro dependency
closure remain undetermined; inventing them would make the offline plan unreliable.
The no-install system-profile path is preferred only if its explicit exception is
accepted and all real-host acceptance criteria pass.
