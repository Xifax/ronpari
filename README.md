# CLI to read manga

One eye in London, other in Paris -- ronpari!

# Idea

*ACTUAL IMPLEMENTATION VARIES*

Simple cli tool to read manga. Imagined usage:

## List current manga [DONE]

> ronpari

```bash
1. Titan on Attack [2/100] [downloaded up to 50]
2. Mieruko [12/60]
3. Something Tabi [30/321]
```

## Continue manga from 2nd chapter [DONE]

> ronpari read 1

```bash
# Continue first manga from chapter 2
# download if no chapter, then
imv /path/to/chapter
OR
ronpari image viewer to /path/to/chapter
```

## Continue manga from specific chapter [DONE]

> ronpari read 2 10

```bash
# Continue second manga from chapter 10
```

## Automatically open next chapter (if possible) [DONE]

> ronpari read 2 --procceed --auto

> ronpari read 2 -pa

## Ask for confirmation to open next chapter [DONE]

> ronpari read 2 --procceed

## List manga and refresh [DONE]

> ronpari status --refresh

## List and download manga [DONE]

> ronpari <manga name> --download

## [TODO] Download active manga

> ronpari download 2

> ronpari download 2 1..100

## [TODO] Archive manga

> ronpari archive 3

## [TODO] Cleanup manga

> ronpari cleanup

```bash
# Removes all chapters before current from disk
```

## [TODO]Path to current chapter

> ronpari path 1

> ronpari path 1 | imv

```bash
# Echo path to latest chapter (optionally download it, if does not exist)
# /home/user/Downloads/manga/Attack/Chapter100
```

## Settings

TODO: refactor this method and options

> ronpari set --path <download_path>

> ronpari set --user <user> --pass <pass>

## [TODO] Set custom command to view images

Currently "imv" is used.

## TODOisms

1. ~~Debug MangaDex.Py downloader (!!!)~~
2. ~~Use custom downloader with Rich progressbar (!!)~~
3. ~~Store status in tinydb (!?)~~
4. ~~Somehow save current chapter and latest chapter when reading (ZSH env variables from imv?)~~
5. Sync with MangaDex via login|passwd (tinydb) [WONTDO]
