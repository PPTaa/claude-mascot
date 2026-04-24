# Fubao raw image sources

All source images are from Wikimedia Commons and carry a Creative Commons
or public-domain license compatible with this project's MIT license. Each
image was downloaded via `Special:FilePath` at width 500, then duplicated
to `_blink` and `_special` variants (v1 has no distinct animation frames —
later iterations can replace these with distinct poses).

See the "File:" page on Wikimedia Commons for each source for exact
license, author, and full-resolution original.

| Emotion | File in `raw/` | Source (Wikimedia Commons) |
|---------|----------------|----------------------------|
| neutral | `neutral_idle.jpg` | https://commons.wikimedia.org/wiki/File:The_butter_panda_sitting.jpg |
| happy | `happy_idle.jpg` | https://commons.wikimedia.org/wiki/File:A_Happy_Panda.jpg |
| angry | `angry_idle.jpg` | https://commons.wikimedia.org/wiki/File:She_Walked_Away_Disappointed_(73005483).jpeg |
| shy | `shy_idle.jpg` | https://commons.wikimedia.org/wiki/File:Giant_panda_(Singapore).jpg |
| sad | `sad_idle.jpg` | https://commons.wikimedia.org/wiki/File:Just_lazing_around_River_Safari.jpg |
| surprised | `surprised_idle.jpg` | https://commons.wikimedia.org/wiki/File:Acrobatics_giant_Panda.jpg |
| love | `love_idle.jpg` | https://commons.wikimedia.org/wiki/File:Cuddling_Pandas.jpg |

For each row above, `_blink.jpg` and `_special.jpg` are byte-identical
copies of `_idle.jpg`. The rendered frame output will therefore look
identical across states for now — replace with distinct source images to
gain real per-state animation.

If you replace any of these images, update this table with the new source
URL and verify the license on the Commons file page.
