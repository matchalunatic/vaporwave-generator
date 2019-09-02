# vaporwave-generator
a    v a p o r w a v e    g r a p h i c s            g e n e r a t o r 

# What is it?

This is a software video synthesizer.
This is a framework for elaborating on this.
This is my toy project and something I use to learn about graphics.

This is python.
This is an homage to the super cool and chill videos made by Switched On SNES.

This is a tribute to the world of analog synths.

# Demo

https://www.youtube.com/watch?v=Bq-zN7QZbig

# Design

All objects are driven by generators (functions that yield values).

At each clock tick the generators are asked for a new value and the objects
vary accordingly.

This allows for various data sources: mathematical functions, user interaction,
randomness, music properties...

Some effects have hardcoded values: this is often temporary or because the
effect only makes sense with these values.

# Plans

Support a better Scene syntax (will always be yaml or toml unless this gets bad)
Support MIDI input for scene tweaking and playing with components parameters
Add more shapes
Add more effects and glitches
Allow the scene components to be driven by sound
Better 3D support

# Original description

So, the idea is to generate chill graphics as in a visualizer for music that
generates glitchy patterns and geometric shapes with varying rythms and some
slight offset, in a lo-fi or vaporwave style.

It's my first toying with graphics programming so it's really crap for the
moment but I hope it will get to something cool somewhere soon.

# Tips
## Run a scene

Launch

./run.sh scene path/to/scene.yml



# General stuff

This is GPLv3+ software.

Feel free to let me know if you use that on your projects. I'd be glad.

## Credits

~ All this bad code done by Matcha Lunatic
Library misused: Pygame ~

i f   y o u  e n j o y    t h i s      
    t h e n

~ please consider supporting my creative programming work

https://www.patreon.com/Matcha

Arwing by dlfon99 / https://www.models-resource.com/custom_edited/starfoxcustoms/model/16500/

