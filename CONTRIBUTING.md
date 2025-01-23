## Contributions

All contributions, whatever their forms, are welcome.

### How ?

* To declare a bug, or ask for an improvement, create an [*issue*] (https://github.com/InseeFrLab/Py-Insee-Data/issues)
* To contribute code or documentation directly, you can use a [*Pull Request*] (https://github.com/InseeFrLab/Py-Insee-Data/pulls). In this case, it is best to link it to an *issue*.
   * The commit messages, as well as the code itself, will preferably be written in English.

### Certificate of Origin

By contributing to this project you agree to the Developer Certificate of Origin (DCO). This document was created by the Linux Kernel community and is a simple statement that you, as a contributor, have the legal right to make the contribution. [See the DCO file for details.](DCO.txt)

Contributors sign-off that they adhere to these requirements by adding a Signed-off-by line to commit messages. For example:

```
This is my commit message

Signed-off-by: Random J Developer <random@developer.example.org>
```

Git even has a -s command line option to append this automatically to your commit message:
```
$ git commit -s -m 'This is my commit message'
```

If you have already made a commit and forgot to include the sign-off, you can amend your last commit to add the sign-off with the following command, which can then be force pushed.
```
git commit --amend -s
```

We use a DCO bot to enforce the DCO on each pull request and branch commits.

### Linting

This project currently uses flake8 and black as pre-commit hooks and will check the code's conformity on the automated tests.
These can be installed via ``pip install flake8 black pre-commit``.

To run the pre-commit hooks on your machine, please run `pre-commit install` locally.

You can then run the pre-commit manually using `pre-commit run --all-files`.

### Licence

By contributing, you agree that your contributions will be licensed under the OPEN LICENSE 2.0.
