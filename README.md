# CUBRIC Food Control

Code to parse and sanitise data produced by the CUBRIC Food Control app.

## Design

Data extraction is divided into two main categories:

* Games
* Questionnaire Questions

These parsing tasks are divided into class hierarchies that inherit from ```DataExtractor```:

* ```GameDataExtractor``` subclasses handle game data extraction
* ```QuestionDataExtractor```subclasses handle questionnaire data extraction


## Games

A ```GameDataExtractor``` subclass handles the extraction, calculation and checking required to process one type of game.

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

## Questionnaire Questions

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
