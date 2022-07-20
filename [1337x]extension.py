# --------------------------------
# File      : [1337x]extension.py
# Author    : Doomlad
# Date      : 07/11/2022
# Info      : Parse a search query via torrent site 1337x.to and its different proxies and
#             prints an array with relevant torrent information to be processed by EZTorrentio.
# --------------------------------
#
# Copyright 2022 Doomlad
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific prior
# written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Build standalone executable with external libs using PyInstaller
# pyinstaller --noconfirm --onefile --console --icon "<path-to-codebase>.ico" --clean --paths "C:/path-to-codebase/venv/Lib/site-packages" --add-data "C:/<path-to-codebase>/i1337x.py;."  "C:/<path-to-codebase>/[1337x]extension.py"

import textwrap
import argparse
from i1337x import py1337x


__version__ = '1.0.0'
argparse_parser = argparse.ArgumentParser(
    formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=40),
    description=textwrap.dedent('''\
        EzTorrentioExtension: [1337x.to]
        --------------------------------
        Parse a search query via torrent site 1337x.to and its different proxies and
        prints an array with relevant torrent information to be processed by EZTorrentio.'''))

argparse_parser.add_argument('query', nargs='?', default=None, help='Enter a search query to be parsed via 1337x or Rarbg torrents.')

argparse_parser.add_argument('-P', '--proxy', default='1337x.to', metavar='<url>', 
    choices=['1337x.to', '1337x.tw', '1377x.to', '1337xx.to', '1337x.st', 'x1337x.ws', 'x1337x.eu', 'x1337x.se', '1337x.is', '1337x.gd'],
    help=textwrap.dedent('''\
        Specify an optional proxy site for 1337x.
            Options: <(default) 1337x.to, 1337x.tw, 1377x.to, 1337xx.to, 
                               1337x.st, x1337x.ws, x1337x.eu, x1337x.se, 
                               1337x.is, 1337x.gd>\n\n'''))

argparse_parser.add_argument('-m', '--method', default='search', metavar='<method>', 
    choices=['search', 'trending', 'top', 'popular', 'browse', 'info'],
    help=textwrap.dedent('''\
        Specify the type of action you would like to perform.
            Options: <(default) search, trending, top, popular, browse, info>\n\n'''))
    
argparse_parser.add_argument('-c', '--category', default=None, metavar='<category>', 
    choices=['Anime', 'Apps', 'Documentaries', 'Games', 'Movies', 'Music', 'Other', 'TV', 'XXX'],
    help=textwrap.dedent('''\
        Specify the type of action you would like to perform, this MUST be set when method=popular/browse.
            Options: <(default) None, Anime, Apps, Documentaries, Games, Movies, Music, Other, TV, XXX>\n\n'''))

argparse_parser.add_argument('-s', '--sortby', default=None, metavar='<criteria>',
    choices=['time', 'size', 'seeders', 'leechers'],
    help=textwrap.dedent('''\
        Specify a sorting criteria when using the search method.
            Options: <(default) None, time, size, seeders, leechers>\n\n'''))

argparse_parser.add_argument('-o', '--order', default='desc', metavar='<order>',
    choices=['desc', 'asc'],
    help=textwrap.dedent('''\
        Specify the order results are retreived. (Descending/Ascending)
            Options: <(default) desc, asc>\n\n'''))

argparse_parser.add_argument('-p', '--page', default=1, metavar='<page>',
    help=textwrap.dedent('''\
        Specify the page number to pull results from. 
            Options: <(default=1) integer>\n\n'''))

argparse_parser.add_argument('-w', '--week', default=False, metavar='<bool>',
    help=textwrap.dedent('''\
        Specify if you want to search for top results of the week. Only applies to trending and popular search methods.
            Options: <(default) false, true>\n\n'''))

argparse_parser.add_argument('-C', '--cookie', default=None, metavar='<cookie>',
    help=textwrap.dedent('''\
        Specify a CloudFlare protected cookie bypass for certain proxies that use it.
        Solve the captcha in your browser and copy the value of the 'cf_clearance' cookie.
            Options: <(default=None) cookie>\n\n'''))

args = argparse_parser.parse_args()
client = py1337x(args.proxy, args.cookie)

# items:
#     name, torrentId, link, seeders, leechers, size, time, uploader, uploaderLink
# currentPage:
# itemCount:
# pageCount:

if args.method == 'search':
    result = client.search(args.query, args.page, args.category, args.sortby, args.order)
    # for page in range(int((result['pageCount']))):
    #     if not page+1 == args.page:
    #         _results = client.search(args.query, page+1, args.category, args.sortby, args.order)
    #         result['items'] += _results['items']
    #         result['itemCount'] = len(result['items'])
    #         result['pageCount'] = '/'

elif args.method == 'trending':
    result = client.trending(args.category, args.week)

elif args.method == 'top':
    result = client.top(args.category)

elif args.method == 'popular':
    result = client.popular(args.category, args.week)

elif args.method == 'browse':
    result = client.browse(args.category, args.page)

elif args.method == 'info':
    result = client.info(args.query)

try:
    print(result)
except NameError:
    print("EzTorrentioExtension [1337x.to]: no arguments provided! try using the -h or --help flag for usage info.")
