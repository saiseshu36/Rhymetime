# Rhyme Time!

A colorful kids? rhyme player built with Flask, HTML/CSS, and JavaScript. Python uses a local TF-IDF pipeline to retrieve rhymes. Human singing is available for Twinkle Twinkle, Mary Had a Little Lamb, Itsy Bitsy Spider, and The Wheels on the Bus. The other rhymes play instrumental sing-along tunes.

## Run the app

1. Install Flask: `python -m pip install -r requirements.txt`
2. Start the app: `python app.py`
3. Open `http://127.0.0.1:5000`.

## Audio credits

- Twinkle Twinkle Little Star: Dcoetzee, [CC0](https://creativecommons.org/publicdomain/zero/1.0/), [source](https://commons.wikimedia.org/wiki/File:Twinkle_Twinkle_Little_Star_-_sung_with_full_lyrics.ogg).
- Mary Had a Little Lamb: Celestianpower, public domain, [source](https://commons.wikimedia.org/wiki/File:Mary_Had_a_Little_Lamb.ogg). The singer?s gender is not identified by the source.
- Itsy Bitsy Spider: [FreeABCSongs.com recording](https://www.freeabcsongs.com/eencyweencyspider), original recording © FreeABCSongs.com. The site permits personal use; it may not be repackaged or resold.
- The Wheels on the Bus: sung by Matt, [Dream English educational MP3](https://www.dreamenglish.com/wheelsonthebus). Copyright Dream English. The site permits use at home, in cars, and in classrooms, but not in commercial projects.
- Old MacDonald Had a Farm: [FreeABCSongs.com recording](https://www.freeabcsongs.com/oldmacdonald), original recording © FreeABCSongs.com. The site permits personal use; it may not be repackaged or resold.
- Row, Row, Row Your Boat: [FreeABCSongs.com recording](https://www.freeabcsongs.com/rowyourboat), original recording © FreeABCSongs.com. The site permits personal use; it may not be repackaged or resold.

The human performances are stored locally in the app so playback does not need a streaming connection. The Itsy Bitsy Spider, Old MacDonald, and Row, Row, Row Your Boat recordings are for personal use and must not be repackaged or resold.
