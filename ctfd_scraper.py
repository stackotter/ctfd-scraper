import argparse

from lib.scraper import Scraper

parser = argparse.ArgumentParser(description='Download challenges from CTFd.')
parser.add_argument('ctfd_url', type=str, help='URL of CTFd site.')
parser.add_argument('out_dir', type=str, help='The output directory for downloaded challenges.')
parser.add_argument('--username', default=None, type=str, help="Username to login with.")
parser.add_argument('--password', default=None, type=str, help="Password to login with.")
parser.add_argument('--json', type=bool, default=False, help="Output challenges to `challenges.json`.")
args = parser.parse_args()

username = args.username or input("Username: ")
password = args.password or input("Password: ")

scraper = Scraper(args.ctfd_url)
scraper.login(username,password)
scraper.download(args.out_dir, export_json=args.json)
