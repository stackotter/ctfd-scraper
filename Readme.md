# CTFd Scraper

CTFd is a popular platform for hosting capture the flag competitions (hacking competitions). This
tool automates downloading the challenges and their associated files.

This fork updates the scraper to python3 and changes the format to suit my liking.

## Usage

```sh
# Provide username and password in command
python ctfd_scraper.py [url] [out_dir] --username [username] --password [password]
```

## Dependencies

```sh
pip install requests json beautifulsoup4 clean-text unidecode
```
