# Archive of the original Sphinx wiki

A byte-for-byte mirror of what is served at
<https://mutanttools.com/docs/_build/html/>, taken 2026-09-21: 198 files, 114
HTML pages plus the `_modules` source views and the theme's static assets.

**This exists because the live copy was backed up nowhere.** It is not in the
`Mutant_Tools` repo, not in `MutantTools WordPress Backup`, not in
`RdM WordPress Backup`. It lived only in `public_html/mutanttools.com/docs/`,
on an account that has already had one full wipe.

And it cannot be rebuilt. `Docs/conf.py` in the Mutant_Tools repo hardcodes
`C://Users//Esteban//Documents//maya//2022//scripts//rigging` and a Maya 2022
site-packages path, and sphinx-autodoc has to import `Mutant_Tools`, which means
importing `maya.cmds`. Losing it would have been permanent.

## This folder does not deploy

It is not listed in `.cpanel.yml`. The live `/docs/` tree is untouched by any
deploy and stays exactly where it is.

## Restoring it

If `public_html/mutanttools.com/docs/` is ever lost, upload the contents of this
folder (minus this README) to that path through cPanel's File Manager. The links
inside are relative, so it works from any directory.

## Why it is still linked

The current wiki at [/wiki/](https://mutanttools.com/wiki/) replaced it and is
generated from the source instead, so it cannot drift. But the old build has
inbound links and bookmarks, so `/docs/` stays online and `/wiki/` points at it.
