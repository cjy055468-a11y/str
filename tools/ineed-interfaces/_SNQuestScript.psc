; Compile-only interface checked against uploaded iNeed PEX. Never install.
Scriptname _SNQuestScript extends Quest
Spell Property _SNAdrenalineSpell Auto
Spell Property _SNWearySpell Auto
Idle Property IdleStop_Loose Auto
Keyword Property Vampire Auto
Keyword Property VendorItemFood Auto
Keyword Property CraftingCookPot Auto
Keyword Property CraftOven Auto
Armor Property DA11RingofNamira Auto
MiscObject Property _SNWaterskin_0 Auto
MiscObject Property _SNWaterskin_Salt Auto
Ingredient Property SaltPile Auto
Potion Property _SNWaterskin_1 Auto
Potion Property _SNWaterskin_2 Auto
Potion Property _SNWaterskin_3 Auto
Potion Property _SNWaterskin_1_Unknown Auto
Potion Property _SNWaterskin_2_Unknown Auto
Potion Property _SNWaterskin_3_Unknown Auto
Sound Property _SNSaltMeatLP Auto
Sound Property _SNWaterskinEmptyLP Auto
FormList Property _SNFood_BloodList Auto
FormList Property _SNFood_DrinkList Auto
FormList Property _SNFood_DrinkSnowList Auto
FormList Property _SNFood_DrinkNoAlcList Auto
FormList Property _SNFood_HeavyList Auto
FormList Property _SNFood_LightList Auto
FormList Property _SNFood_MedList Auto
FormList Property _SNFood_SoupList Auto
FormList Property _SNFood_RawList Auto
FormList Property _SNFood_SkoomaList Auto
FormList Property _SNFood_NoSpoilList Auto
FormList Property _SNFood_IgnoreList Auto
FormList Property _SNTentList Auto
GlobalVariable Property _SNHungerPenalty Auto
GlobalVariable Property _SNThirstPenalty Auto
GlobalVariable Property _SNCannibalToggle Auto
GlobalVariable Property _SNDiseaseStage Auto
GlobalVariable Property _SNDiseaseToggle Auto
GlobalVariable Property _SNFollowerToggle Auto
GlobalVariable Property _SNVampWereToggle Auto
GlobalVariable Property _SNWaterskinEquipToggle Auto
GlobalVariable Property Timescale Auto
Form[] Property FoodInventoryList Auto
Form[] Property FoodRecentList Auto
Float[] Property SatiationList Auto
Float Property SKSEVersion Auto
Float Property TimeUpdate Auto
Float Property HungerRate Auto
Float Property FatigueRate Auto
Float Property ThirstRate Auto
Float Property HungerState Auto
Float Property FatigueState Auto
Float Property ThirstState Auto
Float Property FoodMult Auto
Float Property DrinkMult Auto
Float Property CombatIncreaseNeeds Auto
Float Property TimeInAdrenaline Auto
Int Property VariedDietCount Auto
Int Property TimePassed Auto
Int Property Animations Auto
Int Property BreakableWaterskins Auto
Int Property HasSalmonella Auto
Int Property DrunkAlcohol Auto
Bool Property EnableMod Auto
Bool Property EnableAlcohol Auto
Bool Property EnableSkooma Auto
Bool Property ForceThird Auto
Bool Property AlcoholDehydrates Auto
Bool Property CarriageFastTravel Auto
Bool Property Recategorize Auto
Bool Property IsMale Auto
Bool Property IsSitting Auto
Bool Property IsBedRoll Auto
Bool Property IsWerewolf Auto
Bool Property IsWerewolfHuman Auto
Bool Property PlayerIsWoodelf Auto
Bool Property HarmfulRaw Auto
Bool Property FoodSpoilage Auto
Bool Property JustSlept Auto
Bool Property IsVanillaDiseased Auto
Bool Property ConsumptionNotif Auto
Bool Property IsCooking Auto
Bool Property NoAnimate Auto
Bool Property Restore Auto
String Property RecategorizeStartText Auto
String Property RecategorizeRawText Auto
String Property RecategorizeSoupText Auto
String Property RecategorizeLightText Auto
String Property RecategorizeMedText Auto
String Property RecategorizeHeavyText Auto
String Property RecategorizeDrinkText Auto
String Property RecategorizeDrinkNoAlcText Auto
String Property RecategorizeUnknownText Auto
String Property NoSaltText Auto
String Property NoSaltDecayText Auto
String Property RestText Auto
Actor Property PlayerRef Auto
Function ScanFood() Native
Function CheckCheese(Actor Target, Form Food) Native
Function BreakWater(Actor Target) Native
Function CauseStomachRot(Bool Vanilla = False) Native
Bool Function IsUnsafeLocation() Native
Function Drunk() Native
Function Skooma() Native
Function CheckStatusHunger() Native
Function CheckStatusThirst() Native
Function ModHunger(Float HungerDelta) Native
Function ModFatigue(Float FatigueDelta) Native
Function ModThirst(Float ThirstDelta) Native
Function Maintenance() Native
Event OnUpdate()
EndEvent
