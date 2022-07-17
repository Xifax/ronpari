# Idea

Simple cli tool to read manga. Imagined usage:

## List current manga

> ronpari

```bash
1. Titan on Attack [2/100] [downloaded up to 50]
2. Mieruko [12/60]
3. Something Tabi [30/321]
```

## Continue manga from 2nd chapter

> ronpari 1

```bash
# Continue first manga from chapter 2
# download if no chapter, then
imv /path/to/chapter
OR
ronpari image viewer to /path/to/chapter
```

## Continue manga from specific chapter

> ronpari 2 10

```bash
# Continue second manga from chapter 10
```

## List manga

> ronpari <manga name>

## List and download manga

> ronpari <manga name> --download

## Download all or just range of chapters (next 10?)

> TODO!

## Download active manga

> ronpari download 2

> ronpari download 2 1..100

## Archive manga

> ronpari archive 3

## Cleanup manga

> ronpari cleanup

```bash
# Removes all chapters before current from disk
```

## Path to current chapter

> ronpari path 1

> ronpari path 1 | imv

```bash
# Echo path to latest chapter (optionally download it, if does not exist)
# /home/user/Downloads/manga/Attack/Chapter100
```

## Settings

> ronpari set --path <download_path>

> ronpari set --user <user> --pass <pass>

## TODOisms

1. Debug MangaDex.Py downloader (!!!)
2. Use custom downloader with Rich progressbar (!!)
3. Store status in tinydb (!?)
4. Somehow save current chapter and latest chapter when reading (ZSH env variables from imv?)
5. Sync with MangaDex via login|passwd (tinydb)
