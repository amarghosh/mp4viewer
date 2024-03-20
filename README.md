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
usage: mp4viewer.py [-h] [-o {stdout,gui}] [-e] [-c {on,off}] iso-base-media-file

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

## Sample outputs:
### The default output on the console
&nbsp;&nbsp;\`--- ${\textsf{\color{red}file.mp4}}$  ${\textsf{\color{grey}File}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!\`--- ${\textsf{\color{red}ftyp}}$  ${\textsf{\color{grey}File type}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}major brand}}$: mp42  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}minor version}}$: 1  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}brands}}$: mp42,avc1  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!\`--- ${\textsf{\color{red}moov}}$  ${\textsf{\color{grey}Movie container}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}size}}$: 257878  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!\`--- ${\textsf{\color{red}mvhd}}$  ${\textsf{\color{grey}Movie header}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}creation time}}$: 3531256179  ${\textsf{\color{grey}Wed Nov 25 00:59:18 2015}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}modification time}}$: 3531256179  ${\textsf{\color{grey}Wed Nov 25 00:59:18 2015}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}timescale}}$: 90000  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}duration}}$: 37026990  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}rate}}$: 0x00010000  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}volume}}$: 0x0100  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}matrix}}$: [[65536, 0, 0], [0, 65536, 0], [0, 0, 1073741824]]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}next track id}}$: 3  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!\`--- ${\textsf{\color{red}trak}}$  ${\textsf{\color{grey}Track container}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}size}}$: 135018  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!\`--- ${\textsf{\color{red}tkhd}}$  ${\textsf{\color{grey}Track header}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}creation time}}$: 3531256179  ${\textsf{\color{grey}Wed Nov 25 00:59:18 2015}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}modification time}}$: 3531256179  ${\textsf{\color{grey}Wed Nov 25 00:59:18 2015}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}track id}}$: 1  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}duration}}$: 37026990  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}layer}}$: 0x0000  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}alternate group}}$: 0x0000  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}volume}}$: 0x0000  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}matrix}}$: [[65536, 0, 0], [0, 65536, 0], [0, 0, 1073741824]]  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}width}}$: 94371840  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}height}}$: 94371840  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!\`--- ${\textsf{\color{red}edts}}$  ${\textsf{\color{grey}EDTS}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}size}}$: 36  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;\`--- ${\textsf{\color{red}elst}}$  ${\textsf{\color{grey}Edit list}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}size}}$: 28  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;\`--- ${\textsf{\color{red}mdia}}$  ${\textsf{\color{grey}Media container}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}size}}$: 134882  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!\`--- ${\textsf{\color{red}mdhd}}$  ${\textsf{\color{grey}Media header}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}creation time}}$: 3531256179  ${\textsf{\color{grey}Wed Nov 25 00:59:18 2015}}$  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;!&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ${\textsf{\color{blue}modification time}}$: 3531256179  ${\textsf{\color{grey}Wed Nov 25 00:59:18 2015}}$  

### GTK
![window with gtk treeview](http://2.bp.blogspot.com/-4Uu3eMfMPCQ/UkUpUrfTlKI/AAAAAAAADFs/pxQSh5U81lQ/s1600/mp4viewer_gtk.png)

MP4Viewer uses gtk in graphics mode and requires pygtk3 for viewing results in a window.
This usually comes preinstalled with recent versions of ubuntu.


You can find more similar [MP4 tools in this page](https://github.com/video-dev/community-knowledge-base/blob/master/list-of-iso-bmff-mp4-tools.md)
