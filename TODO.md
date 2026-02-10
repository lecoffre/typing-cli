# TODO — Publish typing-cli on PyPI

## 1. Configure PyPI trusted publishing
- [ ] Create an account on [pypi.org](https://pypi.org/account/register/)
- [ ] Go to **Account settings → Publishing → Add new pending publisher**
- [ ] Fill in:
  - PyPI project name : `typing-cli`
  - Owner : `lecoffre`
  - Repository : `typing-cli`
  - Workflow name : `publish.yml`
  - Environment name : `pypi`

## 2. Create the first release
- [ ] Go to https://github.com/lecoffre/typing-cli/releases/new
- [ ] Tag : `v0.1.0`
- [ ] Title : `v0.1.0`
- [ ] Description : `Initial release — CLI typing test with pixel-art F1 car`
- [ ] Click **Publish release**
- [ ] The GitHub Actions workflow will automatically build and publish to PyPI

## 3. Verify
- [ ] Wait 2-3 minutes for the workflow to finish
- [ ] Check https://pypi.org/project/typing-cli/
- [ ] Test: `pip install typing-cli && typing-cli`

## Result
Anyone can install the app with:
```
pip install typing-cli
```
