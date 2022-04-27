# Cyclops: A real-time web-based constellation visualizer

National Autonomous University of Mexico (https://www.unam.mx/).

- Karime Ochoa Jacinto ([Kadkam8a](https://github.com/Kadkam8a))
- Luis Aaron Nieto Cruz ([LuisAaronNietoCruz](https://github.com/LuisAaronNietoCruz))
- Anton Pashkov ([anton-pashkov](https://github.com/anton-pashkov))

The contents of this repository are licensed under the GNU General Public License version 3. Visit https://www.gnu.org/licenses/gpl-3.0.html for more information.

## Project Definition

### Introduction

The night sky has been a source of astonishment (reflected in the numerous cultural and artistic endeavors of ancient civilizations) and knowledge (such as marine navigation, lunar eclipse predictions, and agricultural activities) for humanity since its inception. 

In his manuscripts, Ptolemy describes the stellar sky as a collection of mythological creatures from the Ancient Greek folklore by drawing imaginary lines connecting different stars with each other. Today, some of these so called constellations are used in horoscopes, and are still widely talked about in popular culture. Nonetheless, with the new scientific discoveries regarding physics (and, in particular, the theory of relativity), we know that, in fact, the firmament we see is nothing more than an image of a distant past. The reason behind this phenomenon is due to the enormous distance separating us from the stars and the speed of light. Thereby, it takes time for the stellar light to reach planet Earth and, as such, there is a delay in the picture we perceive.

### Justification

The purpose of this project is to allow the visualization of the differences between Ptolomean constellations as we can see them with a naked eye and how they would look like if there was no temporal dimension (i.e. the real images of the constellations if we could see the stars in their current positions).

## General Objectives

- Design a data collection API for the Simbad Astronomical Database.
- Implement a data storage system for the collected information.
- Compute the real positions of the stars.
- Compare the observed and real positions of the stars from three constellations: Aquarius, Leo, and Scorpio (corresponding to the horoscopes of the authors of this project).
- Deploy a website in which you can visualize the observed version of the constellations, and their respective real versions produced by our calculations.

## Used Tools

- [Simbad](http://simbad.u-strasbg.fr/simbad/).
- [Python 3](https://www.python.org/).
- [p5.js](https://p5js.org).

## References

- Wikipedia (2022). *Ptolemy*. Retrieved in 08.04.2022 from https://en.wikipedia.org/wiki/Ptolemy
- Wikipedia (2022). *Theory of Relativity*. Retrieved in 08.04.2022 from https://en.wikipedia.org/wiki/Theory_of_relativity
- Wikipedia (2022). *IAU Designated Constellations*. Retrieved in 08.04.2022 from https://en.wikipedia.org/wiki/IAU_designated_constellations
