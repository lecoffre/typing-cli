# TODO — Publish typing-cli on PyPI

## 1. Configure PyPI trusted publishing
- [ ] Crée un compte sur [pypi.org](https://pypi.org/account/register/)
- [ ] Va dans **Account settings → Publishing → Add new pending publisher**
- [ ] Remplis :
  - PyPI project name : `typing-cli`
  - Owner : `lecoffre`
  - Repository : `typing-cli`
  - Workflow name : `publish.yml`
  - Environment name : `pypi`

## 2. Créer la première release
- [ ] Va sur https://github.com/lecoffre/typing-cli/releases/new
- [ ] Tag : `v0.1.0`
- [ ] Title : `v0.1.0`
- [ ] Description : `Initial release — CLI typing test with pixel-art F1 car`
- [ ] Clique **Publish release**
- [ ] Le workflow GitHub Actions build + publie automatiquement sur PyPI

## 3. Vérifier
- [ ] Attends 2-3 minutes que le workflow finisse
- [ ] Vérifie sur https://pypi.org/project/typing-cli/
- [ ] Teste : `pip install typing-cli && typing-cli`

## Résultat
N'importe qui pourra installer l'app avec :
```
pip install typing-cli
```
