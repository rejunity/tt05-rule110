![](../../workflows/gds/badge.svg) ![](../../workflows/docs/badge.svg) ![](../../workflows/test/badge.svg)

# Rule110 Cellular Automata

Cell parallel hardware implementation of the cellular automata in Verilog.
This design executes **over 200 cells** of an elementary cellular automaton **every cycle** applying [Rule 110](https://en.wikipedia.org/wiki/Rule_110) to all of them **in parallel**.

One cycle - one evolution step across all cells!

## First success!
![](./images/passed48.png)

## GDS & Utilisation
Roughly 115 cells with parallel read/write bus can be placed on a single TinyTapeout tile. Without read/write bus, up to 240 cells fit on a single tile!

**Utilisation** with parallel read/write bus (numbers for 2 tiles):
* 232 cells, Tile 1x2 :: **59.84%**, 2119 total cells, 234 DFF, 356 MUX, 281 BUF, **commit 6036188**
* 224 cells, Tile 1x2 :: **57.19%**, 2054 total cells, 226 DFF, 272 MUX, 322 BUF, *commit 34538b6*
* 128 cells, Tile 1x2 :: **31.81%**, 1107 total cells, 130 DFF, 180 MUX, 128 BUF, *commit 89b27ec*
*  64 cells, Tile 1x2 :: **15.85%**,  567 total cells,  66 DFF, 100 MUX,  72 BUF, *commit b9ad400*

**Utilisation** without parallel read/write bus (numbers for 1 tile):
* 128 cells, Tile 1x1 :: **34.56%**, 713 total cells, 129 DFF, **commit 4254a88**
*  32 cells, Tile 1x1 :: **10.49%**, 232 total cells,  33 DFF, *commit e650da8*

## GDS with 240 cells and **59.84%** utilisation.
![](./images/gds_tile1x2_240cells_commit_687474.png)


## What is Tiny Tapeout?

TinyTapeout is an educational project that aims to make it easier and cheaper than ever to get your digital designs manufactured on a real chip.

To learn more and get started, visit https://tinytapeout.com.

### Resources

- [FAQ](https://tinytapeout.com/faq/)
- [Digital design lessons](https://tinytapeout.com/digital_design/)
- [Learn how semiconductors work](https://tinytapeout.com/siliwiz/)
- [Join the community](https://discord.gg/rPK2nSjxy8)

### What next?

- Submit your design to the next shuttle [on the website](https://tinytapeout.com/#submit-your-design). The closing date is **November 4th**.
- Edit this [README](README.md) and explain your design, how it works, and how to test it.
- Share your GDS on Twitter, tag it [#tinytapeout](https://twitter.com/hashtag/tinytapeout?src=hashtag_click) and [link me](https://twitter.com/matthewvenn)!
