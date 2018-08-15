# foodcontrol

Code to parse/ sanitise and mangle data for Leah's Project

### The data per-processor is at: 

```
dataimport/scripts/stop.py
```

You'll need to change the file location on line 123 to whatever file you're loading in.

## New Development

The ```extract``` branch contains new development in the ```extract``` folder, which is new development and refactoring of the ```dataimport/scripts/stop.py``` script into a set of extractor classes stored in the ```extractors``` folder.

Each ```DataExtractor``` subclass handles the extraction, calculation and checking required to process one type of game.


The games are:

* Stop
* Restraint
* NAStop
* NARestraint
* GStop
* GRestraint
* Double
* MCII
* GoalVis
* Measures
* Eligibility
* AdditionalInfo
* VirtualSupermarket

Extraction is driven by the ```extract.py``` script.
