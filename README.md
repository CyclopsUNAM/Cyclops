# Cyclops: A real-time web-based constellation visualizer

National Autonomous University of Mexico (https://www.unam.mx/).

- Karime Ochoa Jacinto ([Kadkam8a](https://github.com/Kadkam8a))
- Luis Aaron Nieto Cruz ([LuisAaronNietoCruz](https://github.com/LuisAaronNietoCruz))
- Anton Pashkov ([anton-pashkov](https://github.com/anton-pashkov))

The contents of this repository are licensed under the GNU General Public License version 3. Visit https://www.gnu.org/licenses/gpl-3.0.html for more information.

## Introduction

The night sky has been a source of astonishment (reflected in the numerous cultural and artistic endeavors of ancient civilizations) and knowledge (such as marine navigation, lunar eclipse predictions, and agricultural activities) for humanity since its inception. 

In his manuscripts, Ptolemy describes the stellar sky as a collection of mythological creatures from the Ancient Greek folklore by drawing imaginary lines connecting different stars with each other. Today, some of these so called constellations are used in horoscopes, and are still widely talked about in popular culture. Nonetheless, with the new scientific discoveries regarding physics (and, in particular, the theory of relativity), we know that, in fact, the firmament we see is nothing more than an image of a distant past. The reason behind this phenomenon is due to the enormous distance separating us from the stars and the speed of light. Thereby, it takes time for the stellar light to reach planet Earth and, as such, there is a delay in the picture we perceive.

The purpose of this project is to allow the visualization of the differences between Ptolomean constellations as we can see them with a naked eye and how they would look like if there was no temporal dimension (i.e. the real images of the constellations if we could see the stars in their current positions). The execution of the project is distributed in four parts (data collection, data storage, calculation, and visualiation), each of which runs on a different computer system.

## Objectives

- Design a data collection software for the SIMBAD Astronomical Database, which will fetch the information of all the stars in a given IAU designated constellation.
- Implement a data storage system for the collected information.
- Compute the real positions of the stars.
- Compare the observed and real positions of the stars from three constellations: Aquarius, Scorpio, and Leo (corresponding to the horoscopes of the authors of this project).
- Deploy a website in which you can visualize the observed version of the constellations, and their respective real versions produced by our calculations.

## Used Tools

- [SIMBAD](http://simbad.u-strasbg.fr/simbad/).
- [Python 3](https://www.python.org/).

## Methodology

### Part I. Data Collection

The Set of Identifications, Measurements and Bibliography for Astronomical Data ([SIMBAD](https://simbad.cds.unistra.fr/simbad/)) is perhaps one of the most comprehensive astronomical databases available to the public. It stores detailed information on many cosmic objects (such as stars and planets), as well as bibliographic data, providing several ways to query this information. For this project, we will use the [script execution query mode](https://simbad.cds.unistra.fr/simbad/sim-fscript) as it enables us to build our automatic data collection system in a simpler way. By using the `query id` command followed by the name of an object (such as a star), you can fetch the information available on the given object. Furthermore, when submitting this kind of script, you are automatically redirected to a URL in the form of `https://simbad.cds.unistra.fr/simbad/sim-script?submit=submit+script&script=query+id+[OBJECT NAME]`. Thus, we can open the URL through Python for any object by employing the `urlopen` function from the `urllib.request` library. For instance, to fetch the data on the Alpha Centauri star, we would type:

```python
from urllib.request import urlopen
data = urlopen('https://simbad.cds.unistra.fr/simbad/sim-script?submit=submit+script&script=query+id+alpha+centauri')
```

The `starinfo` function from the `spider.py` module does this process automatically for any given object, returning a Python dictionary of the data required for our project. In particular, this data includes:

- Aquí
- irá
- una
- lista
- de
- datos
- (con su descripción)

However, SIMBAD contains no information on constellations, so we had to search for it elsewhere. Because different authors and websites provided slightly distinct configurations for the constellations, our team decided to use the information from a single source to ensure its consistency: Philip M. Bagnall's book titled *The Star Atlas Companion*. From it, we created a JSON file, in which, for every constellation [^1], we list each star and their respective neighbors. The contents of this file can be found in `constellations.json`. So, every time a request is made for a particular constellation, our software will automatically download the data corresponding to the stars found in the given constellation. This process is implemented in the `no_name_function` function from the `spider.py` module.

### Part II. Data Storage



### Part III. Calculations



### Part IV. Visualization
Probandooo




## References

- Bagnall, P. M. (2012). *The Star Atlas Companion: What You Need to Know about the Constellations*. Springer Science+Business Media. DOI: [10.1007/978-1-4614-0830-7](https://doi.org/10.1007/978-1-4614-0830-7)
- Wikipedia (2022). *Ptolemy*. Retrieved in 08.04.2022 from https://en.wikipedia.org/wiki/Ptolemy
- Wikipedia (2022). *Theory of Relativity*. Retrieved in 08.04.2022 from https://en.wikipedia.org/wiki/Theory_of_relativity
- Wikipedia (2022). *IAU Designated Constellations*. Retrieved in 08.04.2022 from https://en.wikipedia.org/wiki/IAU_designated_constellations

[^1]: As of May 2022, the project only includes three constellations: Aquarius, Scorpius, and Leo.
