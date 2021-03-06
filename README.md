**Outdated code base, development now takes place on [geokelone package](https://github.com/adbar/geokelone)**


## Project basics

Prototype for toponym extraction in historical texts written in German, as seen in:

* Barbaresi, A., article to appear in book on *Visual Linguistics*.
* Digital Humanities 2017 (Montréal, Canada): Barbaresi, A., [Toponyms as Entry Points into a Digital Edition: Mapping Die Fackel (1899-1936)](https://www.conftool.pro/dh2017/index.php?page=browseSessions&form_session=344&presentations=show), *Proceedings of Digital Humanities 2017*, to appear.
* Digital Humanities 2016 (Cracow, Poland): Barbaresi, A. and Biber, H., [Extraction and Visualization of Toponyms in Diachronic Text Corpora](https://hal.archives-ouvertes.fr/hal-01348696/document), *Digital Humanities 2016  Conference Abstracts*, pp. 732-734.
* CLARIN-D CA-3 Hands-On Session (Hamburg, Germany): Barbaresi, A., [Extraktion und Visualisierung von Ortsnamen im Deutschen Textarchiv](https://www.clarin-d.net/de/aktuelles/forum-ca3-2016/hands-on-poster-demos).
* DHd 2016 (Leipzig, Germany): Barbaresi, A., [Visualisierung von Ortsnamen im Deutschen Textarchiv](https://halshs.archives-ouvertes.fr/halshs-01287931/document), in *Proceedings of DHd 2016*, pp. 264-267.


## Files currently in the repository

* ~~Scripts released under [GNU GPLv3](https://www.gnu.org/licenses/gpl.html) license~~
   1. ~~Extraction of place names (work in progress! stable version only)~~
   2. ~~Preparation of data from [Geonames](http://www.geonames.org/) (used as a fallback)~~

* Curated registers containing place names released under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) license, 2016 versions, *update pending*
   1. Manually curated historical lists: continental, state, and region levels
   2. Semi-automatically completed list: cities and towns
   3. Data gathered from Wikipedia (CC-BY license), *to be cleared and uploaded*


## Sources

### Data

#### Wikipedia

* [List of German exonyms](https://en.wikipedia.org/wiki/List_of_German_exonyms)
* [Verzeichnis:International/Städtenamen](https://de.wiktionary.org/wiki/Verzeichnis:International/St%C3%A4dtenamen)
* [Liste der Listen deutschsprachiger Bezeichnungen nicht deutschsprachiger Orte](https://de.wikipedia.org/wiki/Liste_der_Listen_deutschsprachiger_Bezeichnungen_nicht_deutschsprachiger_Orte)
* [Kategorie:Historische Landschaft oder Region in Europa](https://de.wikipedia.org/wiki/Kategorie:Historische_Landschaft_oder_Region_in_Europa)
* etc.

#### Other

* [Verzeichnis der mehrsprachigen Ortsnamen (Südost- und Osteuropa)](http://www.sulinet.hu/oroksegtar/data/magyarorszagi_nemzetisegek/nemetek/die_donauschwaben/pages/019_Anhang_I.htm) [archive](http://web.archive.org/web/20160602013439/http://www.sulinet.hu/oroksegtar/data/magyarorszagi_nemzetisegek/nemetek/die_donauschwaben/pages/019_Anhang_I.htm)
* [OME-Lexikon Orte und Städte](http://ome-lexikon.uni-oldenburg.de/orte/) [archive](http://web.archive.org/web/20151104075126/http://ome-lexikon.uni-oldenburg.de/orte/)
* [WW II European Gazetteer](http://ww2db.com/other.php?other_id=31) [archive](http://web.archive.org/web/20160303203323/http://ww2db.com/other.php?other_id=31)
* [Austro-Hungarian Army Peacetime Locations and Recruiting Areas 1866](http://www.austro-hungarian-army.co.uk/loc1866.htm) [archive](http://web.archive.org/web/20150516025238/http://www.austro-hungarian-army.co.uk/loc1866.htm)
* [Österreichisch-Ungarische Monarchie, Königreiche und Länder](http://agso.uni-graz.at/marienthal/gramatneusiedl/07_oesterreich_ungarn.htm) [archive](http://web.archive.org/web/20160403164137/http://agso.uni-graz.at/marienthal/gramatneusiedl/07_oesterreich_ungarn.htm)


### Stop lists

* https://tools.wmflabs.org/persondata/data/pd_dump.txt
* http://gfds.de/vornamen/beliebteste-vornamen/
* https://de.wiktionary.org/wiki/Verzeichnis:Deutsch/Liste_der_h%C3%A4ufigsten_m%C3%A4nnlichen_Vornamen_Deutschlands
* https://de.wiktionary.org/wiki/Verzeichnis:Deutsch/Liste_der_h%C3%A4ufigsten_weiblichen_Vornamen_Deutschlands
* https://de.wiktionary.org/wiki/Verzeichnis:Deutsch/Liste_der_h%C3%A4ufigsten_Nachnamen_Deutschlands
* https://de.wiktionary.org/wiki/Verzeichnis:Deutsch/Liste_der_h%C3%A4ufigsten_Nachnamen_%C3%96sterreichs
* https://de.wikipedia.org/wiki/Liste_deutschsprachiger_Schriftsteller
* https://de.wikisource.org/wiki/Liste_der_Autoren


### Method

* https://www.mediawiki.org/wiki/Extension:GeoData#API
* [Haversine formula](https://en.wikipedia.org/wiki/Haversine_formula) and [implementation](http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points#4913653)
* https://github.com/asciimoo/exrex


## Additional infos

Thanks to Logan Pecinovsky (BBAW, Berlin) and Judith Brottrager (ÖAW, Vienna) for helping with the curation of the lists.

**Outdated code base, development now takes place on [geokelone package](https://github.com/adbar/geokelone)**
