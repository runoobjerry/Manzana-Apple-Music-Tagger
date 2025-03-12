# __Manzana Apple Music Tagger__

A python program to fetch credits info from apple music about albums, songs and music-videos and tag MP4 and M4A files using those credits info.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dropcreations/Manzana-Apple-Music-Tagger/main/assets/manzana__dark.png">
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/dropcreations/Manzana-Apple-Music-Tagger/main/assets/manzana__light.png">
  <img alt="Apple Music" src="https://raw.githubusercontent.com/dropcreations/Manzana-Apple-Music-Tagger/main/assets/manzana__light.png">
</picture>

## __Features__

- Can tag an album or a single track or a music-video
- Embeds and saves artworks
- Saves animated artworks if available
- Saves time-synced lyrics if you have an Apple Music subscription
- Also tags the lyrics to the media file if available
- Adds newly released role-credits.

## __Required__

- [MP4Box](https://gpac.wp.imt.fr/downloads/)

## __How to use?__

### __# for all users__

First of all clone this project or download the project as a zip file and extract it to your pc. (or you can see [Releases](https://github.com/dropcreations/Manzana-Apple-Music-Tagger/releases))

```
git clone https://github.com/runoobjerry/Manzana-Apple-Music-Tagger.git && cd Manzana-Apple-Music-Tagger
```

Install required modules for python (use `pip3` if `pip` doesn't work for you)

```
pip install -r requirements.txt
```

Then you have to ready your files for tagging. So, if you are tagging a complete album you must have the tracks in M4A format (with AAC or ALAC codec) and then rename each file as `01, 02, 03,...` (number must have 2-digits) respectively to the order of tracks in Apple Music. For an example, assume you have an album called __"Doja Cat - Planet Her"__ in __M4A__ format and they are currently renamed as below

```
Doja Cat - Planet Her (https://music.apple.com/us/album/planet-her/1573475827)
  │
  ├── Alone.m4a
  ├── Been Like This.m4a
  ├── Get Into It (Yuh).m4a
  ├── I Don't Do Drugs.m4a
  ├── Imagine.m4a
  ├── Kiss Me More.m4a
  ├── Love To Dream.m4a
  ├── Naked.m4a
  ├── Need to Know.m4a
  ├── Options.m4a
  ├── Payday.m4a
  ├── Women.m4a
  └── You Right.m4a
```

So, now you have to rename those as below.

```
Doja Cat - Planet Her (https://music.apple.com/us/album/planet-her/1573475827)
  │
  ├── Alone.m4a               as  12.m4a
  ├── Been Like This.m4a      as  09.m4a
  ├── Get Into It (Yuh).m4a   as  04.m4a
  ├── I Don't Do Drugs.m4a    as  06.m4a
  ├── Imagine.m4a             as  11.m4a
  ├── Kiss Me More.m4a        as  13.m4a
  ├── Love To Dream.m4a       as  07.m4a
  ├── Naked.m4a               as  02.m4a
  ├── Need to Know.m4a        as  05.m4a
  ├── Options.m4a             as  10.m4a
  ├── Payday.m4a              as  03.m4a
  ├── Women.m4a               as  01.m4a
  └── You Right.m4a           as  08.m4a
```

After renaming tracks, open terminal inside the folder that tracks included and run below command (Use `py` or `python3` if `python` doesn't work for you)

```
python manzana.py [album_url]
```

or if you are opening the terminal outside that folder, use below command

```
python manzana.py --input [folder_path] [album_url]
```

If you are tagging a single file, don't need to rename it. just use below command

```
python manzana.py --input [file_path] [song_url]
```

If you want to get animated cover if available, use `--animartwork` or `-an` argument

```
python manzana.py -an [album or song url]
```

Get help using `-h` or `--help` command

```
usage: manzana.py [-h] [-v] [-sc {2,3}] [-an] [-cn] [-ln] [-sv] [-i INPUT] url

Manzana: Apple Music Tagger

positional arguments:
  url                   Apple Music URL

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -sc {2,3}, --sync {2,3}
                        Timecode's ms point count in synced lyrics. (default: 2)
  -an, --animartwork    Download the animated artwork if available. (default: False)
  -cn, --no-cover       Don't save album artwork. (default: False)
  -ln, --no-lrc         Don't save time-synced lyrics as a .lrc file. (default: False)
  -sv, --skip-video     Skip videos in an album. (default: False)
  -i INPUT, --input INPUT
                        Folder or file path for m4a/mp4 media files. (default: Current working directory)
```

### __# for subscribed users__

Get your Apple Music cookies from web browser and search for `media-user-token` and get it.

|Domain|Include subdomains|Path|Secure|Expiry|Name|Value
|---|---|---|---|---|---|---|
|.apple.com|TRUE|/|FALSE|0|geo|##|
|.apple.com|TRUE|/|TRUE|0|dslang|##-##|
|.apple.com|TRUE|/|TRUE|0|site|###|
|.apple.com|TRUE|/|TRUE|0|myacinfo|#####...|
|.music.apple.com|TRUE|/|TRUE|1680758167|commerce-authorization-token|#####...|
|.apple.com|TRUE|/|FALSE|1715317057|itspod|##|
|.music.apple.com|TRUE|/|TRUE|1681361859|media-user-token|#####...|
|.music.apple.com|TRUE|/|TRUE|1681361859|itre|#|
|.music.apple.com|TRUE|/|TRUE|1681361859|pldfltcid|#####...|
|.music.apple.com|TRUE|/|TRUE|1681361859|pltvcid|#####...|
|.music.apple.com|TRUE|/|TRUE|1681361859|itua|##|

You need to add `mediaUserToken` to get `lyricist` and `lyrics` and also to save `timeSyncedLyrics` as a `.lrc` file.<br>

Please create a `txt` file named `mediaUserToken` in the `\utils` folder, and fill in the token you got on the web page, the program will automatically read the token in it.

Program will ask you for the `storefront` and `language` when you run it. You can fill in the metadata for the region and language you want to obtain.

If you want to change the `language` or `mediaUserToken` , run below command to clear the configuration and run the program again.

```
python manzana.py reset
```

When saving time synced lyrics, timestamps are in `00:00.00` format. If you want to get it in `00:00.000` format set `--sync` as `3` as below

```
python manzana.py --sync 3 [album or song url]
```

If you don't want to get time synced lyrics as `.lrc` file, use `--no-lrc` argument.

```
python manzana.py --no-lrc [album or song url]
```

### Sample

```
Format                                   : MPEG-4
Format profile                           : Apple audio with iTunes info
Codec ID                                 : M4A  (isom/iso5/hlsf/cmfc/ccea/M4A /mp42)
File size                                : 32.5 MiB
Duration                                 : 4 分 55 秒
Overall bit rate mode                    : 动态码率 (VBR)
Overall bit rate                         : 921 kb/s
Album                                    : I'm O.K.
Album/Performer                          : 陶喆
Part/Position                            : 1
Part/Total                               : 1
Track name                               : 小镇姑娘
Track name/Position                      : 3
Track name/Total                         : 13
Performer                                : 陶喆
Composer                                 : 陶喆
Arranger                                 : 陶喆
Lyricist                                 : 陶喆
Producer                                 : 陶喆
Label                                    : Gold Typhoon Taiwan
Genre                                    : 国语流行
ContentType                              : Music
Recorded date                            : 1999-08-24
Encoded date                             : 2022-03-01 02:45:32 UTC
Tagged date                              : 2022-03-01 02:45:33 UTC
ISRC                                     : TWC219900003
Copyright                                : ℗ 1999 Gold Typhoon Music Co. Ltd.
Cover                                    : Yes
UPC                                      : 825646245383
Guitar                                   : Bruce Watson
Mixing Engineer                          : Craig Burbidge
Bass                                     : Reggie Hamilton
Background Vocals                        : 陶喆
Lead Vocals                              : 陶喆
Programming                              : 陶喆
Other Instrument                         : 陶喆
Mastering Engineer                       : Maggie Chen / Stephen Marcussen
Engineer                                 : 陶喆 / Craig Burbidge
Vocal Producer                           : 陶喆 / 王治平 / 李咏恩
```

## About me

Hi, You might recognize me as GitHub's [dropcreations](https://github.com/dropcreations).

__Other useful python scripts done by me__

| Project        | Github location                                |
|----------------|------------------------------------------------|
| mkvextractor   | https://github.com/dropcreations/mkvextractor  |
| flactagger     | https://github.com/dropcreations/flactagger    |
| mp4tagger      | https://github.com/dropcreations/mp4tagger     |
| mkvtagger      | https://github.com/dropcreations/mkvtagger     |

<br>

- __NOTE: If you found any issue using this program, mention in issues section__

## Support

[!["Buy Me A Coffee"](https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0)](https://ko-fi.com/dropcodes)
