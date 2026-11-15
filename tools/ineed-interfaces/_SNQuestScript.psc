; Compile-only interface extracted from the uploaded iNeed source. Do not install.
Scriptname _SNQuestScript extends Quest
Spell Property _SNAdrenalineSpell Auto
Spell Property _SNWearySpell Auto
Keyword Property Vampire Auto
FormList Property _SNTentList Auto
GlobalVariable Property _SNHungerPenalty Auto
GlobalVariable Property _SNThirstPenalty Auto
GlobalVariable Property _SNVampWereToggle Auto
GlobalVariable Property _SNWaterskinEquipToggle Auto
Float Property SKSEVersion Auto
Float Property TimeUpdate Auto
Float Property HungerRate Auto
Float Property FatigueRate Auto
Float Property ThirstRate Auto
Float Property TimeInAdrenaline Auto
Int Property TimePassed Auto
Int Property HasSalmonella Auto
Int Property DrunkAlcohol Auto
Bool Property EnableMod Auto
Bool Property CarriageFastTravel Auto
Bool Property IsMale Auto
Bool Property IsSitting Auto
Bool Property IsBedRoll Auto
Bool Property IsWerewolf Auto
Bool Property JustSlept Auto
String Property RestText Auto
Actor Property PlayerRef Auto
Function ScanFood() Native
Bool Function IsUnsafeLocation() Native
Function ModHunger(Float HungerDelta) Native
Function ModFatigue(Float FatigueDelta) Native
Function ModThirst(Float ThirstDelta) Native
Event OnUpdate()
EndEvent
