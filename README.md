# tetris_school

The tetris game we were to write in 10th grade on winter vacation

It's Python 3-only an it depends on Pygame, so you'll have to run it with an old
version of Python, like python3.1

Probably has a couple of bugs lurking around. I'm not striving to identify and
fix them, because the code style is quite ugly, and it seems like I was starting
to approach the callback hell.

It is quite interesting however that I, faced with the need of async
architecture, came up with the idea of callbacks, non-blocking functions, and
essentially the event loop (I used pygame's built-in one, but it wasn't supposed
to be used for async things). I certainly knew there were threads, but they
seemed like an overkill for my simple needs of being able to close the window
while animating.

Animations were implemented by simply looping and drawing frames one-by-one, so
they are likely to be quite fast on modern computers (mine was pretty old, and I
was developing on a VM that had an older Python version than my host machine).

It took some time (and lots of spaghetti code) to implement intelligent borders,
rotation that doesn't accumulate error. The way colors were generated is
strange, too.

The most interesting thing is the bot. I'm not going to dive into the details
here, so see it for yourself if you manage to get it running.

Anyway, have fun and please don't blame me!
