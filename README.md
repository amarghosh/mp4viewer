![Pylint](https://github.com/amarghosh/mp4viewer/actions/workflows/pylint.yml/badge.svg)

MP4Viewer
=========

MP4Viewer is an ISO base media file format viewer.
It parses the isobmf file and displays the metadata on the console or in a separate window.
The definitions of structures used in the code can be found in ~the publicly available standard~ (it is not free to download anymore) standard [ISO/IEC 14496-12 - ISO base media file format](http://standards.iso.org/ittf/PubliclyAvailableStandards/index.html)

## Basic usage

```bash
./parse.sh [-h] [-o {stdout,gui}] [-e] [-c {on,off}] file.mp4
```
## Supported flags
```
./parse.sh -h
usage: showboxes.py [-h] [-o {stdout,gui}] [-e] [-c {on,off}] iso-base-media-file

Process iso-bmff file and list the boxes and their contents

positional arguments:
  iso-base-media-file   Path to iso media file

options:
  -h, --help            show this help message and exit
  -o {stdout,gui}       output format
  -e, --expand-arrays   do not truncate long arrays
  -c {on,off}, --color {on,off}
                        turn on/off colors in console based output; on by default
```

## Screenshots:
![shell output](http://3.bp.blogspot.com/-APb-4LsE9LM/UkUoome4U4I/AAAAAAAADFk/ZkTpd7JkF24/s1600/mp4viewer_shell.png)
![window with gtk treeview](http://2.bp.blogspot.com/-4Uu3eMfMPCQ/UkUpUrfTlKI/AAAAAAAADFs/pxQSh5U81lQ/s1600/mp4viewer_gtk.png)

MP4Viewer uses gtk in graphics mode and requires pygtk3 for viewing results in a window.
This usually comes preinstalled with recent versions of ubuntu.


You can find more similar [MP4 tools in this page](https://github.com/video-dev/community-knowledge-base/blob/master/list-of-iso-bmff-mp4-tools.md)
