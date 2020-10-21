Releasing thriftcli is rather straightforward:
1. Ensure you are using the correct virtualenv, and that you are able to run thriftcli from source
2. Ensure you have PyPI account, and is a maintainer for thriftcli
3. Do a `rm -rf dist` to clear out your dist dir
4. Edit `setup.py`, bumping up the version, and then merge it
5. Go to Github, and create a new release. Run `git log tag1..tag2` to put relevant info in the release notes.
6. Install Twine: `pip install twine`
7. Run `python setup.py sdist bdist_wheel`. Check that files are inside the `dist` dir.
8. Do a `tar tzf dist/thriftcli-VERSION.tar.gz` and check that the files are there.
9. Do a `twine check dist/*`. It should pass, warnings are ok.
10. Run `twine upload --repository-url https://test.pypi.org/legacy/ dist/*` if you have access to test pypi.
11. Release it! `twine upload dist/*`
12. Install it! `pip install thriftcli==VERSION`
13. Run it by hitting an actual server.
14. Done!

The above is based on https://realpython.com/pypi-publish-python-package/.
