# CUBRIC Food Control

Code to parse and sanitise data produced by the CUBRIC Food Control app.

## Design

The parsing tasks are divided into classes that inherit from ```DataExtractor```.


## Games

A ```DataExtractor``` subclass handles the extraction, calculation and checking required to process one type of game.

The game types are:

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

## Questions

A ```QuestionDataExtractor``` subclass handles the extraction, calculation and checking required to process one type of question.

The question types are:

* Freq
* Taste
* Attract
* EX
* Will
* Mood
* IMP
* FoodIMP
* EMREG
* Goals
* Intent
* Person
* Effect
* MINDF
* RESTR

## Extraction

Extraction is driven by the ```extract.py``` script.
