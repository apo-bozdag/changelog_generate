## Changelog generator

Only the 4 tags mentioned will appear in the version system.
`added`,`removed`,`changed`,`fixed`

commit sample;

* `git commit -m"added: blabla.."`
* `git commit -m"removed: blabla.."`
* `git commit -m"changed: blabla.."`
* `git commit -m"fixed: blabla.."`


It is created in the tag according to the version you choose while creating the changelog.

* `python changelog_generate.py`
* `git push --tags`

Finally, don't forget to push your changelog.md & config.ini files.
