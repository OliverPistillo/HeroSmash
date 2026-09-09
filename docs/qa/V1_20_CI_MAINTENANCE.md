# Official Actions runtime maintenance

The v1.19 runner warning identifies checkout@v4, setup-python@v5, setup-node@v4
and upload-artifact@v4 as Node20 actions. On 2026-09-09 the official v6 action.yml
files were retrieved and all four explicitly declare runs.using=node24.

The workflow pins these official v6 commits:

- checkout d23441a48e516b6c34aea4fa41551a30e30af803
- setup-python ece7cb06caefa5fff74198d8649806c4678c61a1
- setup-node 249970729cb0ef3589644e2896645e5dc5ba9c38
- upload-artifact b7c566a772e6b6bfb58ed0dc250532a479d7789f

Used inputs (fetch-depth/lfs/python-version/node-version/name/path) are supported;
ubuntu-latest satisfies the Node24 runner requirement. The existing tested Node
20.19.6 workload and Python3.12 remain explicit, independent of the Actions runtime.
No fork or local Node installation is introduced. v7 releases exist, but their ESM/
additional behavior changes are unnecessary for this scoped deprecation fix.

Sources are the official repositories and exact versioned action.yml files:
[checkout](https://github.com/actions/checkout/blob/d23441a48e516b6c34aea4fa41551a30e30af803/action.yml),
[setup-python](https://github.com/actions/setup-python/blob/ece7cb06caefa5fff74198d8649806c4678c61a1/action.yml),
[setup-node](https://github.com/actions/setup-node/blob/249970729cb0ef3589644e2896645e5dc5ba9c38/action.yml),
[upload-artifact](https://github.com/actions/upload-artifact/blob/b7c566a772e6b6bfb58ed0dc250532a479d7789f/action.yml).
Remote execution and warning absence must be checked after this separate commit.
