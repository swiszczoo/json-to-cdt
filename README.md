# JSON to CDT

A simple Python script for authoring binary CD-Text files from JSON descriptions of their contents. All fields and metadata are supported. Generated output complies with Red Book Compact Disc Digital Audio specification.

## Output

For the provided `example.json`, the output looks like this:
```
Offset(h) 00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F 10 11

00000000  80 00 00 00 41 6C 62 75 6D 20 74 69 74 6C 65 20 8C D3  €...Album title ŚÓ
00000012  80 00 01 0C 76 65 72 79 20 6C 6F 6E 67 00 54 72 40 1C  €...very long.Tr@.
00000024  80 01 02 02 61 63 6B 20 31 00 54 72 61 63 6B 20 24 09  €...ack 1.Track $.
00000036  80 02 03 06 32 00 54 72 61 63 6B 20 33 00 00 00 43 48  €...2.Track 3...CH
00000048  81 00 04 00 41 6C 62 75 6D 20 61 72 74 69 73 74 30 26  ....Album artist0&
0000005A  81 00 05 0C 00 41 72 74 69 73 74 00 41 72 74 69 21 07  .....Artist.Arti!.
0000006C  81 02 06 04 73 74 00 41 72 74 69 73 74 00 00 00 D5 9E  ....st.Artist...Őž
0000007E  86 00 07 00 41 4C 42 55 4D 30 30 31 00 00 00 00 89 6B  †...ALBUM001....‰k
00000090  8E 00 08 00 30 30 30 30 30 30 30 30 30 30 30 30 D4 4C  Ž...000000000000ÔL
000000A2  8E 00 09 0C 31 00 50 4C 54 53 54 32 34 30 30 30 36 B2  Ž...1.PLTST240006˛
000000B4  8E 01 0A 0A 30 31 00 50 4C 54 53 54 32 34 30 30 63 F4  Ž...01.PLTST2400cô
000000C6  8E 02 0B 09 30 30 32 00 50 4C 54 53 54 32 34 30 B4 05  Ž...002.PLTST240´.
000000D8  8E 03 0C 08 30 30 30 33 00 00 00 00 00 00 00 00 0A 6B  Ž...0003.........k
000000EA  8F 00 0D 00 00 01 03 03 04 03 00 00 00 00 01 00 43 27  Ź...............C'
000000FC  8F 01 0E 00 00 00 00 00 00 00 05 03 0F 00 00 00 B9 59  Ź...............ąY
0000010E  8F 02 0F 00 00 00 00 00 20 00 00 00 00 00 00 00 23 48  Ź....... .......#H

```
