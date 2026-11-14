Scriptname _JSW_FB_HandlerScript extends ReferenceAlias

Actor Property PlayerRef  Auto
_JSW_FB_MeterWidget Property Widget  Auto

GlobalVariable Property Enabled  Auto            ; True if temperature is checked, false otherwise
GlobalVariable Property PollingInterval  Auto    ; The number of real-time seconds temperature is checked
GlobalVariable Property Sunrise  Auto            ; The time of day when the sun begins radiating additional warmth
GlobalVariable Property Sunset  Auto             ; The time of day when the sun stops radiating additional warmth
GlobalVariable Property HeatSourceRadius  Auto   ; The number of units in which a heat source radiates warmth
GlobalVariable Property WarmDelta  Auto          ; The amount of body temperature gained per polling interval in a warm area
GlobalVariable Property ComfortableDelta  Auto   ; The amount of body temperature gained per polling interval in a comfortable area
GlobalVariable Property NoneDelta  Auto          ; The amount of body temperature gained per polling interval in a neutral area
GlobalVariable Property CoolDelta  Auto          ; The amount of body temperature lost per polling interval in a cool area
GlobalVariable Property ColdDelta  Auto          ; The amount of body temperature lost per polling interval in a cold area
GlobalVariable Property FreezingDelta  Auto      ; The amount of body temperature lost per polling interval in a freezing area
GlobalVariable Property FoodDelta  Auto          ; The amount of body temperature increase when consuming a warming item
GlobalVariable Property HealthDebuff  Auto       ; Enables or disables debuffs on the health attribute
GlobalVariable Property StaminaDebuff  Auto      ; Enables or disables debuffs on the stamina attribute
GlobalVariable Property MagickaDebuff  Auto      ; Enables or disables debuffs on the magicka attribute
GlobalVariable Property RegenDebuff  Auto        ; The range of body temperature in which attribute regen is disabled
GlobalVariable Property DamageDebuff  Auto       ; The range of body temperature in which attribute damage is taken
GlobalVariable Property DamageDelta  Auto        ; The percentage of base damage taken per polling interval when in a damage range
GlobalVariable Property EnableVampires  Auto     ; Support cold adjustment for vampires
GlobalVariable Property EnableWerewolves  Auto   ; Support cold adjustment for werewolves
GlobalVariable Property EnableLiches  Auto       ; Support cold adjustment for liches (eg. Undeath)
GlobalVariable Property WidgetWidth  Auto        ; The pixel width of the widget
GlobalVariable Property WidgetHeight  Auto       ; The pixel height of the widget
GlobalVariable Property WidgetTop  Auto          ; The Y position of the temperature widget
GlobalVariable Property WidgetLeft  Auto         ; The X position of the temperature widget
GlobalVariable Property WidgetShown  Auto        ; True if the widget is visible, false otherwise
GlobalVariable Property WidgetFade  Auto         ; True if the widget fades when fully warm
GlobalVariable Property WidgetHotKey  Auto       ; The key code for showing or hiding the widget
GlobalVariable Property WarmingAnimation  Auto   ; Enables or disables a warming animation near heat sources
GlobalVariable Property DetectClothing  Auto     ; Automatically detects the warmth factor of clothing
GlobalVariable Property VerboseFeedback  Auto    ; Additional feedback effects and notifications for current status

FormList Property InteriorColdZones  Auto        ; Interior areas with a location that present as cold
FormList Property InteriorColdCells  Auto        ; Non-location interior areas that present as cold
FormList Property StandardHeatSources  Auto      ; Objects which radiate heat
FormList Property WarmingFoods  Auto             ; Food and drink with warming properties
FormList Property ExcludedFoods  Auto            ; Food and drink with no warming properties
FormList Property WarmClothing  Auto             ; Clothing and armors that provide some protection from the cold
FormList Property VeryWarmClothing  Auto         ; Clothing and armors that provide excellent protection from the cold
FormList Property ExcludedClothing  Auto         ; Clothing and armors that provide no protection from the cold

FormList Property VampireRaces  Auto             ; Supported vampire races for cold adjustment
FormList Property WerewolfRaces  Auto            ; Supported werewolf races for cold adjustment
FormList Property LichRaces  Auto                ; Supported lich races for cold adjustment

MagicEffect[] Property FlameCloak  Auto

Spell Property RegenDebuffAbilityHealth  Auto    ; Ability that disables base health regen
Spell Property RegenDebuffAbilityStamina  Auto   ; Ability that disables base stamina regen
Spell Property RegenDebuffAbilityMagicka  Auto   ; Ability that disables base magicka regen

ImageSpaceModifier Property IMODEnterCold  Auto  ; Visual indicator that the ambient temperature is colder
ImageSpaceModifier Property IMODEnterWarm  Auto  ; Visual indicator that the ambient temperature is warmer

Idle Property IdleWarmHandsStanding  Auto
Idle Property IdleWarmHandsCrouched  Auto
Idle Property IdleStop_Loose  Auto

Message Property AddFoodMsg  Auto
Message Property AddClothingMsg  Auto

int Property TEMP_WARM =        2  AutoReadOnly
int Property TEMP_COMFORTABLE = 1  AutoReadOnly
int Property TEMP_NONE =        0  AutoReadOnly
int Property TEMP_COOL =       -1  AutoReadOnly
int Property TEMP_COLD =       -2  AutoReadOnly
int Property TEMP_FREEZING =   -3  AutoReadOnly

int Property WeatherNone =     -1  AutoReadOnly
int Property WeatherPleasant =  0  AutoReadOnly
int Property WeatherCloudy =    1  AutoReadOnly
int Property WeatherRainy =     2  AutoReadOnly
int Property WeatherSnow =      3  AutoReadOnly

int Property AddItemWarming =    0  AutoReadOnly ; Menu option for a food item that has warming properties
int Property AddItemNotWarming = 1  AutoReadOnly ; Menu option for a food item that has no warming properties

int Property PreviousTemp = 0  Auto              ; Represents the previous ambient temperature when changing areas
int Property CurrentTemp = 0  Auto               ; Represents the current ambient temperature
float Property PreviousBodyTemp = 1.0  Auto      ; Represents the player's previous temperature
float Property BodyTemp = 1.0  Auto              ; Represents the player's current temperature

bool _idlePlaying = false
int _idleCycles = 0
bool _coolingDefaultsUpdated = false

event OnInit()
{Ensure everything is sorted when loading starting for the first time}
	Debug.Notification("正在启动 Frostbite 体温系统……")
	
	UpgradeCoolingDefaults()
	InitializeCompatibility()
	InitializeWidget()
	
	RegisterForKey(WidgetHotKey.GetValueInt())
	RegisterForModEvent("FrostbiteWidgetReset", "OnFrostbiteWidgetReset")
	RegisterForModEvent("FrostbiteNearHeatSource", "OnFrostbiteNearHeatSource")
	RegisterForSingleUpdate(1.0)
endEvent

event OnPlayerLoadGame()
{Ensure everything is sorted when loading an existing save}
	UpgradeCoolingDefaults()
	InitializeCompatibility()
	InitializeWidget()
	
	RegisterForKey(WidgetHotKey.GetValueInt())
	RegisterForModEvent("FrostbiteWidgetReset", "OnFrostbiteWidgetReset")
	RegisterForModEvent("FrostbiteNearHeatSource", "OnFrostbiteNearHeatSource")
	RegisterForSingleUpdate(1.0)
endEvent

event OnUpdate()
{Run polling interval updates}
	if (Enabled.GetValueInt())
		PreviousBodyTemp = BodyTemp
		PreviousTemp = CurrentTemp
		CurrentTemp = GetCurrentTemperature(PlayerRef.GetPositionX(), PlayerRef.GetPositionY(), PlayerRef.GetPositionZ()) as int
		
		; Signify a change of ambient temperature if needed
		if (PreviousTemp != CurrentTemp)
			if (CurrentTemp == TEMP_WARM)
				RunVerboseFeedback("这里很温暖。")
			elseIf (CurrentTemp == TEMP_COMFORTABLE)
				RunVerboseFeedback("这里的温度很舒适。")
			elseIf (CurrentTemp == TEMP_NONE)
				RunVerboseFeedback("这里不冷不热。")
			elseIf (CurrentTemp == TEMP_COOL)
				RunVerboseFeedback("这里有些凉。", IMODEnterCold)
			elseIf (CurrentTemp == TEMP_COLD)
				RunVerboseFeedback("这里很冷。", IMODEnterCold)
			elseIf (CurrentTemp == TEMP_FREEZING)
				RunVerboseFeedback("这里寒冷刺骨。", IMODEnterCold)
			endIf
		endIf
		
		float delta = 0.0
		
		; Identify the ambient temperature delta
		if (CurrentTemp == TEMP_WARM)
			delta = WarmDelta.GetValue()
		elseIf (CurrentTemp == TEMP_COMFORTABLE)
			delta = ComfortableDelta.GetValue()
		elseIf (CurrentTemp == TEMP_NONE)
			delta = NoneDelta.GetValue()
		elseIf (CurrentTemp == TEMP_COOL)
			delta = -CoolDelta.GetValue()
		elseIf (CurrentTemp == TEMP_COLD)
			delta = -ColdDelta.GetValue()
		elseIf (CurrentTemp == TEMP_FREEZING)
			delta = -FreezingDelta.GetValue()
		endIf
		
		BodyTemp += delta
		
		; Clamp the final body temperature
		if (BodyTemp < 0.0)
			BodyTemp = 0.0
		elseIf (BodyTemp > 1.0)
			BodyTemp = 1.0
		endIf
		
		; Signify a change of body temperature if needed
		if (PreviousBodyTemp != BodyTemp && BodyTemp >= 1.0)
			RunVerboseFeedback("你已经完全暖和起来了。", IMODEnterWarm)
		endIf
		
		UpdateWidget()
		UpdateDebuff()
	else
		ClearColdDebuffs()
		StopWarmingAnimation()
	endIf
	
	RegisterForSingleUpdate(PollingInterval.GetValue())
endEvent

event OnKeyDown(int keyCode)
{Handle the hotkey presses}
	if (!Enabled.GetValueInt())
		return
	endIf
	
	if (!Utility.IsInMenuMode())
		if (keyCode == WidgetHotKey.GetValueInt())
			if (WidgetShown.GetValueInt() == 1)
				Widget.Alpha = 0.0
				WidgetShown.SetValueInt(0)
			else
				Widget.Alpha = 100.0
				WidgetShown.SetValueInt(1)
			endIf
		endIf
	endIf
endEvent

event OnFrostbiteWidgetReset(string eventName, string strArg, float numArg, Form sender)
{Refresh the local UI and clear effects when the system has been disabled.}
	if (!Enabled.GetValueInt())
		ClearColdDebuffs()
		StopWarmingAnimation()
	elseIf (!WarmingAnimation.GetValueInt())
		StopWarmingAnimation()
	endIf
	InitializeWidget()
	UpdateWidget()
endEvent

event OnControlDown(string control)
{Every control registered by the warming idle must also cancel that idle.}
	StopWarmingAnimation()
endEvent

event OnFrostbiteNearHeatSource(string eventName, string strArg, float numArg, Form sender)
{Play an appropriate warming idle animation when reasonable}
	if (!Enabled.GetValueInt() || !WarmingAnimation.GetValueInt())
		StopWarmingAnimation()
		return
	endIf
	
	if (!_idlePlaying)
		if (!PlayerRef.GetAnimationVariableBool("IsFirstPerson") && \
			!PlayerRef.IsInCombat() && \
			!PlayerRef.IsWeaponDrawn() && \
			!Utility.IsInMenuMode())
			
			if (_idleCycles < 2)
				_idleCycles += 1
			else
				bool idleStarted = false
				if (PlayerRef.IsSneaking())
					idleStarted = PlayerRef.PlayIdle(IdleWarmHandsCrouched)
				else
					idleStarted = PlayerRef.PlayIdle(IdleWarmHandsStanding)
				endif
				if (!idleStarted)
					_idleCycles = 0
					return
				endIf
				
				_idlePlaying = true
				
				RegisterForControl("Forward")
				RegisterForControl("Back")
				RegisterForControl("Strafe Left")
				RegisterForControl("Strafe Right")
				RegisterForControl("Move")
				RegisterForControl("Activate")
				RegisterForControl("Ready Weapon")
				RegisterForControl("Jump")
				RegisterForControl("Sneak")
			endIf
		endIf
	elseIf (_idlePlaying && (PlayerRef.IsInCombat() || PlayerRef.IsWeaponDrawn() || Utility.IsInMenuMode()))
		StopWarmingAnimation()
	endif
endEvent

event OnObjectEquipped(Form akBaseObject, ObjectReference akReference)
{Handle item usage and consumption}
	if (!Enabled.GetValueInt())
		return
	endIf
	
	if (akBaseObject as Potion)
		if ((akBaseObject as Potion).IsFood())
			CheckUnknownFood(akBaseObject)
		endIf
		
		if (WarmingFoods.Find(akBaseObject) != -1)
			BodyTemp += FoodDelta.GetValue()
			
			; Clamp the final body temperature
			if (BodyTemp < 0.0)
				BodyTemp = 0.0
			elseIf (BodyTemp > 1.0)
				BodyTemp = 1.0
			endIf
			
			UpdateWidget()
			UpdateDebuff()
		endIf
	elseIf (akBaseObject as Armor)
		int slot = (akBaseObject as Armor).GetSlotMask()
		
		if ((Math.LogicalAnd(slot, 0x00000002) == 0x00000002 && (akBaseObject.HasKeywordString("ClothingHead") || akBaseObject.HasKeywordString("ArmorHelmet"))) || \
			Math.LogicalAnd(slot, 0x00000004) == 0x00000004 || \
			Math.LogicalAnd(slot, 0x00000008) == 0x00000008 || \
			Math.LogicalAnd(slot, 0x00010000) == 0x00010000)
			
			CheckUnknownClothing(akBaseObject)
		endIf
	endIf
endEvent

float function GetCurrentTemperature(float posX, float posY, float posZ)
{Identify the current ambient temperature based on weather, time of day, swimming, and local heat sources}
	float temp = 0.0

	if (!PlayerRef.IsInInterior())
		Weather currentWeather = Weather.GetCurrentWeather()
		int weatherClass = WeatherNone
	
		if (currentWeather == none)
			temp = TEMP_COOL
		else
			weatherClass = currentWeather.GetClassification()
			
			if (weatherClass == WeatherNone)
				temp = TEMP_NONE
			elseIf (weatherClass == WeatherPleasant)
				temp = TEMP_COOL
			elseIf (weatherClass == WeatherCloudy)
				temp = TEMP_COOL
			elseIf (weatherClass == WeatherRainy)
				temp = TEMP_COLD
			elseIf (weatherClass == WeatherSnow)
				temp = TEMP_COLD
			endIf
		endIf
		
		float hour = GetCurrentHourOfDay()
		
		if (weatherClass == WeatherPleasant && (hour >= Sunrise.GetValue() && hour <= Sunset.GetValue()))
			; Increase warmth when in reasonably direct sunlight
			temp += 1.0
		elseIf (hour < Sunrise.GetValue() || hour > Sunset.GetValue())
			; Reduce warmth when the sun is below a viewing angle
			temp -= 1.0
		endIf
	else
		if (InteriorColdZones.Find(PlayerRef.GetCurrentLocation()) != -1 || InteriorColdCells.Find(PlayerRef.GetParentCell()) != -1)
			temp = TEMP_COLD
		else
			temp = TEMP_WARM
		endIf
	endif
	
	; Check for local warming and cooling sources
	if (PlayerRef.IsSwimming())
		StopWarmingAnimation()
		; Reduce temperature when actively swimming
		temp -= 2.0
	elseIf (Game.FindClosestReferenceOfAnyTypeInList(StandardHeatSources, posX, posY, posZ, HeatSourceRadius.GetValue()) != none)
		; The temperature is warm when near a fire
		temp = TEMP_WARM
		SendModEvent("FrostbiteNearHeatSource")
	else
		StopWarmingAnimation() ; Also handles leaving the fire without a movement key.
	endIf
	
	; Check for warm clothing
	temp += GetClothingWarmthDelta(PlayerRef.GetWornForm(0x00000002) as Armor)       ; Head
	temp += GetClothingWarmthDelta(PlayerRef.GetWornForm(0x00000004) as Armor)       ; Body
	temp += GetClothingWarmthDelta(PlayerRef.GetWornForm(0x00000008) as Armor)       ; Hands
	temp += GetClothingWarmthDelta(PlayerRef.GetWornForm(0x00010000) as Armor, true) ; Cloak
	
	; Werewolves and undead do not suffer from the cold
	if (EnableVampires.GetValueInt() && VampireRaces.HasForm(PlayerRef.GetRace()))
		temp = TEMP_NONE
	elseIf (EnableWerewolves.GetValueInt() && WerewolfRaces.HasForm(PlayerRef.GetRace()))
		temp = TEMP_NONE
	elseIf (EnableLiches.GetValueInt() && LichRaces.HasForm(PlayerRef.GetRace()))
		temp = TEMP_NONE
	endIf
	
	; Check for warming magic effects
	int i = FlameCloak.Length
	
	while (i)
		i -= 1
		
		if (PlayerRef.HasMagicEffect(FlameCloak[i]))
			temp = TEMP_WARM
		endIf
	endWhile
	
	; Clamp the final temperature
	if (temp < TEMP_FREEZING)
		temp = TEMP_FREEZING
	elseIf (temp > TEMP_WARM)
		temp = TEMP_WARM
	endIf
	
	return temp
endFunction

float function GetClothingWarmthDelta(Armor akWornItem, bool ignoreDetection = false)
{Identify the warmth delta for the given item}
	float warmthDelta = 0.0
	
	if (!akWornItem)
		; Don't bother if nothing is in the armor slot
		return warmthDelta
	endIf
	
	if (!ignoreDetection && DetectClothing.GetValueInt())
		if (akWornItem.HasKeywordString("ArmorHeavy"))
			warmthDelta = 0.5
		elseIf (akWornItem.HasKeywordString("ArmorLight"))
			warmthDelta = 0.25
		elseIf (akWornItem.HasKeywordString("ArmorClothing"))
			warmthDelta = 0.125
		endIf
	else
		if (VeryWarmClothing.HasForm(akWornItem))
			warmthDelta = 0.5
		elseIf (WarmClothing.HasForm(akWornItem))
			warmthDelta = 0.25
		elseIf (ExcludedClothing.HasForm(akWornItem))
			warmthDelta = 0.125
		endIf
	endIf
	
	return warmthDelta
endFunction

float function GetCurrentHourOfDay()
{Identify the current 24 hour time of day}
	float now = Utility.GetCurrentGameTime()
	
	now -= Math.Floor(now)
	now *= 24
	
	return now
endFunction

function InitializeCompatibility()
{Check for and apply compatibility patches for third party mods}
	; Check for Campfire heat sources
	if (Game.GetModByName("Campfire.esm") != 255)
		StandardHeatSources.AddForm(Game.GetFormFromFile(0x00040013, "Campfire.esm") as Activator)
		StandardHeatSources.AddForm(Game.GetFormFromFile(0x000328b9, "Campfire.esm") as Activator)
		StandardHeatSources.AddForm(Game.GetFormFromFile(0x00033e67, "Campfire.esm") as Activator)
		StandardHeatSources.AddForm(Game.GetFormFromFile(0x00033e69, "Campfire.esm") as Activator)
	endIf
	
	; Check for Hunterborn warming foods
	if (Game.GetModByName("Hunterborn.esp") != 255)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e08, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e09, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e0b, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e0f, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e11, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e15, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e17, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e19, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e27, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03017e4b, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x03029db9, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030314c9, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030314D1, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x0303fd68, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030402d7, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030402da, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030402dc, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030402de, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030402e0, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030402e2, "Hunterborn.esp") as Potion)
		WarmingFoods.AddForm(Game.GetFormFromFile(0x030402e4, "Hunterborn.esp") as Potion)
	endIf
	
	; Check for lich races from Undeath
	if (Game.GetModByName("Undeath.esp") != 255)
		LichRaces.AddForm(Game.GetFormFromFile(0x0401772a, "Undeath.esp") as Race)
	endIf
	
	; Check for lich races from Path of Transcendence
	if (Game.GetModByName("The Path of Transcendence.esp") != 255)
		LichRaces.AddForm(Game.GetFormFromFile(0x05038357, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x050e0e47, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0522bd61, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x05240166, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x05240167, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0524a378, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0524a379, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0524f47d, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0524f47e, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0524f482, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0524f486, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0524f487, "The Path of Transcendence.esp") as Race)
		LichRaces.AddForm(Game.GetFormFromFile(0x0537fd2b, "The Path of Transcendence.esp") as Race)
	endIf
endFunction

function CheckUnknownFood(Form akBaseObject)
{Check for and attempt to add unknown food items}
	if (!WarmingFoods.HasForm(akBaseObject) && !ExcludedFoods.HasForm(akBaseObject))
		int result = AddFoodMsg.Show()
		
		if (result == AddItemWarming)
			WarmingFoods.AddForm(akBaseObject)
		elseIf (result == AddItemNotWarming)
			ExcludedFoods.AddForm(akBaseObject)
		endIf
	endIf
endFunction

function CheckUnknownClothing(Form akBaseObject)
{Check for and attempt to add unknown clothing}
	if (DetectClothing.GetValueInt())
		return
	endIf
	
	if (!WarmClothing.HasForm(akBaseObject) && !VeryWarmClothing.HasForm(akBaseObject) && !ExcludedClothing.HasForm(akBaseObject))
		int result = AddClothingMsg.Show()
		
		if (result == 0)
			ExcludedClothing.AddForm(akBaseObject)
		elseIf (result == 1)
			WarmClothing.AddForm(akBaseObject)
		elseIf (result == 2)
			VeryWarmClothing.AddForm(akBaseObject)
		endIf
	endIf
endFunction

function InitializeWidget()
{Apply current settings to the widget}
	Widget.Width = WidgetWidth.GetValue()
	Widget.Height = WidgetHeight.GetValue()
	Widget.HAnchor = "left"
	Widget.VAnchor = "top"
	Widget.X = WidgetLeft.GetValueInt()
	Widget.Y = WidgetTop.GetValueInt()
	
	if (WidgetShown.GetValueInt() == 1)
		Widget.Alpha = 100.0
	else
		Widget.Alpha = 0.0
	endIf
	
	Widget.SetPercent(BodyTemp)
	Widget.FillDirection = "right"
	Widget.SetColors(0xffffff,0xffffff)
endFunction

function UpdateWidget()
{Update the current widget status}
	if (CurrentTemp == TEMP_WARM)
		Widget.SetColors(0xff0000, 0xff0000)
	elseIf (CurrentTemp == TEMP_COMFORTABLE)
		Widget.SetColors(0xff9999, 0xff9999)
	elseIf (CurrentTemp == TEMP_NONE)
		Widget.SetColors(0xffffff, 0xffffff)
	elseIf (CurrentTemp == TEMP_COOL)
		Widget.SetColors(0x0080ff, 0x0080ff)
	elseIf (CurrentTemp == TEMP_COLD)
		Widget.SetColors(0x0000ff, 0x0000ff)
	elseIf (CurrentTemp == TEMP_FREEZING)
		Widget.SetColors(0xff00ff, 0xff00ff)
	endIf
	
	if (WidgetShown.GetValueInt() && WidgetFade.GetValueInt())
		if (BodyTemp >= 1.0)
			Widget.FadeTo(0.0, 2.0)
		else
			Widget.FadeTo(100.0, 2.0)
		endIf
	endIf
	
	Widget.SetPercent(BodyTemp)
endFunction

function UpdateDebuff()
{Apply or remove debuffs according to body temp and settings}
	if (BodyTemp > RegenDebuff.GetValue())
		; Remove all debuffs
		ClearColdDebuffs()
	elseIf (BodyTemp > DamageDebuff.GetValue())
		; Apply the regen debuff if it's not already applied
		if (HealthDebuff.GetValueInt())
			PlayerRef.AddSpell(RegenDebuffAbilityHealth, false)
		else
			PlayerRef.RemoveSpell(RegenDebuffAbilityHealth)
		endIf
		
		if (StaminaDebuff.GetValueInt())
			PlayerRef.AddSpell(RegenDebuffAbilityStamina, false)
		else
			PlayerRef.RemoveSpell(RegenDebuffAbilityStamina)
		endIf
		
		if (MagickaDebuff.GetValueInt())
			PlayerRef.AddSpell(RegenDebuffAbilityMagicka, false)
		else
			PlayerRef.RemoveSpell(RegenDebuffAbilityMagicka)
		endIf
		
		Widget.StartFlash()
	else
		float frostResist = PlayerRef.GetActorValue("FrostResist")
		
		; Apply the damage debuff
		; The regen debuff remains as well
		if (HealthDebuff.GetValueInt())
			float actorValue = PlayerRef.GetBaseActorValue("Health")
			float damage = (actorValue * DamageDelta.GetValue()) / 100.0
			
			; Adjust for frost resistance
			damage = damage * (1.0 - (frostResist / 100.0))
			
			if (damage < 0.0)
				damage = 0.0
			endIf
			
			PlayerRef.AddSpell(RegenDebuffAbilityHealth, false)
			PlayerRef.DamageActorValue("Health", damage)
		else
			PlayerRef.RemoveSpell(RegenDebuffAbilityHealth)
		endIf
		
		if (StaminaDebuff.GetValueInt())
			float actorValue = PlayerRef.GetBaseActorValue("Stamina")
			float damage = (actorValue * DamageDelta.GetValue()) / 100.0
			
			; Adjust for frost resistance
			damage = damage * (1.0 - (frostResist / 100.0))
			
			if (damage < 0.0)
				damage = 0.0
			endIf
			
			PlayerRef.AddSpell(RegenDebuffAbilityStamina, false)
			PlayerRef.DamageActorValue("Stamina", damage)
		else
			PlayerRef.RemoveSpell(RegenDebuffAbilityStamina)
		endIf
		
		if (MagickaDebuff.GetValueInt())
			float actorValue = PlayerRef.GetBaseActorValue("Magicka")
			float damage = (actorValue * DamageDelta.GetValue()) / 100.0
			
			; Adjust for frost resistance
			damage = damage * (1.0 - (frostResist / 100.0))
			
			if (damage < 0.0)
				damage = 0.0
			endIf
			
			PlayerRef.AddSpell(RegenDebuffAbilityMagicka, false)
			PlayerRef.DamageActorValue("Magicka", damage)
		else
			PlayerRef.RemoveSpell(RegenDebuffAbilityMagicka)
		endIf
		
		Widget.StartFlash()
	endIf
endFunction

function RunVerboseFeedback(string msg, ImageSpaceModifier imodEffect = none)
{Apply verbose feedback effects}
	if (!VerboseFeedback.GetValueInt())
		return
	endIf
	
	if (imodEffect)
		imodEffect.Apply()
		ImageSpaceModifier.RemoveCrossFade(1.0)
	endIf
	
	Debug.Notification(msg)
endFunction

function UpgradeCoolingDefaults()
{Upgrade untouched original defaults once; preserve later or custom MCM settings.}
	if (_coolingDefaultsUpdated)
		return
	endIf
	if (CoolDelta.GetValue() == 0.005)
		CoolDelta.SetValue(0.0075)
	endIf
	if (ColdDelta.GetValue() == 0.01)
		ColdDelta.SetValue(0.015)
	endIf
	if (FreezingDelta.GetValue() == 0.025)
		FreezingDelta.SetValue(0.05)
	endIf
	_coolingDefaultsUpdated = true
endFunction

function ClearColdDebuffs()
{Remove only this mod's three local player abilities, without repeated network echoes.}
	if (PlayerRef.HasSpell(RegenDebuffAbilityHealth))
		PlayerRef.RemoveSpell(RegenDebuffAbilityHealth)
	endIf
	if (PlayerRef.HasSpell(RegenDebuffAbilityStamina))
		PlayerRef.RemoveSpell(RegenDebuffAbilityStamina)
	endIf
	if (PlayerRef.HasSpell(RegenDebuffAbilityMagicka))
		PlayerRef.RemoveSpell(RegenDebuffAbilityMagicka)
	endIf
endFunction

function StopWarmingAnimation()
{Cancel only the warming idle started by this local player alias.}
	if (_idlePlaying)
		_idlePlaying = false
		PlayerRef.PlayIdle(IdleStop_Loose)
	endIf
	_idleCycles = 0
	UnregisterForAllControls()
endFunction
