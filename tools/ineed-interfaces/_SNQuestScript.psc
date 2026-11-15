; Compile-only interface checked against uploaded iNeed main PEX. Never install.
Scriptname _SNQuestScript extends Quest
Spell Property _SNAdrenalineSpell Auto
Spell Property _SNWearySpell Auto
Spell Property _SNOldConfigSpell Auto
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
Potion Property _SNSnowPile Auto
Sound Property _SNWaterskinWaterBodyRefillLP Auto
Sound Property _SNSaltMeatLP Auto
Sound Property _SNSnowGatherLP Auto
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
FormList Property _SNSnowStatList Auto
FormList Property _SNTentList Auto
GlobalVariable Property _SNHungerRate Auto
GlobalVariable Property _SNThirstRate Auto
GlobalVariable Property _SNFatigueRate Auto
GlobalVariable Property _SNAutoHungerToggle Auto
GlobalVariable Property _SNAutoThirstToggle Auto
GlobalVariable Property _SNHungerPenalty Auto
GlobalVariable Property _SNThirstPenalty Auto
GlobalVariable Property _SNFollowerNeedsToggle Auto
GlobalVariable Property _SNCannibalToggle Auto
GlobalVariable Property _SNDiseaseStage Auto
GlobalVariable Property _SNDiseaseToggle Auto
GlobalVariable Property _SNFollowerToggle Auto
GlobalVariable Property _SNFollowerPurchaseToggle Auto
GlobalVariable Property _SNFoodRemovalToggle Auto
GlobalVariable Property _SNValuedHarvestsToggle Auto
GlobalVariable Property _SNValuedHarvestsDialogueToggle Auto
GlobalVariable Property _SNVampWereToggle Auto
GlobalVariable Property _SNAdrenalineToggle Auto
GlobalVariable Property _SNWaterskinEquipToggle Auto
GlobalVariable Property _SNUnknownAllToggle Auto
GlobalVariable Property _SNHorseNeedsToggle Auto
GlobalVariable Property _SNCarryWeightMag Auto
GlobalVariable Property Timescale Auto
Race Property WoodelfRace Auto
Race Property WoodelfRaceVampire Auto
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
Float Property HungerVol Auto
Float Property FatigueVol Auto
Float Property ThirstVol Auto
Float Property FoodMult Auto
Float Property DrinkMult Auto
Float Property WidgetAlpha Auto
Float Property FollowerHungerRate Auto
Float Property FollowerThirstRate Auto
Float Property CombatIncreaseNeeds Auto
Float Property RawFreshness Auto
Float Property LightFreshness Auto
Float Property MedFreshness Auto
Float Property HeavyFreshness Auto
Float Property TimeInAdrenaline Auto
Int Property WidgetOrient Auto
Int Property WidgetPos Auto
Int Property NotifHUD Auto
Int Property WidgetXOffset Auto
Int Property WidgetYOffset Auto
Int Property VariedDietCount Auto
Int Property TimePassed Auto
Int Property DefaultColor Auto
Int Property Animations Auto
Int Property FoodPriority Auto
Int Property BreakableWaterskins Auto
Int Property HasSalmonella Auto
Int Property DrunkAlcohol Auto
Bool Property ForceFollowerConsume Auto
Bool Property FoodWeight Auto
Bool Property FoodNoEffect Auto
Bool Property FoodPrice Auto
Bool Property NotifAutoText Auto
Bool Property AnimationsFollowers Auto
Bool Property RefillAnimate Auto
Bool Property EnableMod Auto
Bool Property EnableAlcohol Auto
Bool Property EnableSkooma Auto
Bool Property ForceThird Auto
Bool Property AlcoholDehydrates Auto
Bool Property CarriageFastTravel Auto
Bool Property Recategorize Auto
Bool Property NotifText Auto
Bool Property IsMale Auto
Bool Property IsSitting Auto
Bool Property IsBedRoll Auto
Bool Property IsWerewolf Auto
Bool Property IsWerewolfHuman Auto
Bool Property PlayerIsWoodelf Auto
Bool Property Death Auto
Bool Property SetLeveledLists Auto
Bool Property HarmfulRaw Auto
Bool Property NoSalt Auto
Bool Property IsInWater Auto
Bool Property FoodSpoilage Auto
Bool Property JustSlept Auto
Bool Property DisplayPercent Auto
Bool Property WidgetHide Auto
Bool Property IsVanillaDiseased Auto
Bool Property ConsumptionNotif Auto
Bool Property DiseaseNotif Auto
Bool Property WidgetDisease Auto
Bool Property IsCooking Auto
Bool Property NoAnimate Auto
Bool Property Restore Auto
Bool Property EnableActionsSpell Auto
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
String Property SpoilageReminder Auto
String Property NoWaterSourceText Auto
String Property RestText Auto
String Property DrinkWaterText Auto
String Property UnknownWaterText Auto
Actor Property PlayerRef Auto
Function SetPerspective(Bool FirstPersonText = False) Native
Function ScanFood() Native
Function CheckCheese(Actor Target, Form Food) Native
Bool Function IsInSaltWater() Native
Function BreakWater(Actor Target) Native
Function SetPotionLeveledLists(Bool Revert = False) Native
Function DiseaseRoll() Native
Function CauseStomachRot(Bool Vanilla = False) Native
Function CureDisease() Native
Bool Function RefillUnknown(Actor Target) Native
Bool Function Refill(Actor Target, Bool Animate = False) Native
Bool Function IsSafeLocation(Location CurrentLoc) Native
Bool Function IsUnsafeLocation() Native
Function Drink(Actor Target) Native
Bool Function AutoEat(Actor Target, Bool Text = True, Bool Remove = False) Native
Function AutoDrink(Actor Target, Bool Text = True) Native
Function Drunk() Native
Function Skooma() Native
Function CheckStatusHunger() Native
Function CheckStatusThirst() Native
Function CheckStatus() Native
Function CheckInventory() Native
Function ModHunger(Float HungerDelta) Native
Function ModFatigue(Float FatigueDelta) Native
Function ModThirst(Float ThirstDelta) Native
Function FoodLeveledList() Native
Function Maintenance() Native
Function Restart() Native
Function DisableMod() Native
Function EnableMod() Native
Event OnUpdate()
EndEvent
