# Claudia

Claudia is Claude's cousin. She lives in your terminal as pixel art, and she has one piece of wisdom to share:

> Liefde is zoals een scheet: als je het forceert, zit er kak tussen.
>
> *Love is like a fart: if you force it, there's shit in it.*

![Claudia blinking, winking, sending hearts up and farting](preview.gif)

Type `claudia` and she:

1. types her line into a speech bubble while she talks,
2. blinks and winks,
3. sends a few hearts up,
4. farts: PRRRT!, a green cloud, stink lines and a very embarrassed face, until the cloud drifts off.

The show takes about seven seconds; Ctrl+C stops it early.

## Install

Claudia is a single Python 3 script without dependencies. Put it somewhere on your `PATH`:

```sh
mkdir -p ~/.local/bin
curl -fsSL https://raw.githubusercontent.com/PieterLuypaert/claudia/main/claudia -o ~/.local/bin/claudia
chmod +x ~/.local/bin/claudia
```

She needs a terminal with 256 colours and looks best with true colour (`COLORTERM=truecolor`, which most modern terminals set).

## Usage

```sh
claudia                            # her line, with the full show
claudia "Goeiemorgen!"             # she says your text instead
git log -1 --format=%s | claudia   # she says whatever you pipe in
```

When the output is not a terminal, `NO_COLOR` is set, or the terminal is too small, she is printed once in grey shades and stands still. In a narrow terminal the speech bubble moves above her.

## Preview

`preview.gif` is rendered from the script itself:

```sh
python3 scripts/make-preview.py
```

## License

[MIT](LICENSE). Just for fun, not affiliated with Anthropic.
