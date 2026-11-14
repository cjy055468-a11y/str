Scriptname _JSW_FB_ConfigScript extends SKI_ConfigBase

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
FormList Property WarmingFoods  Auto             ; Food and drink with warming properties
FormList Property ExcludedFoods  Auto            ; Food and drink with no warming properties
FormList Property WarmClothing  Auto             ; Clothing and armors that provide some protection from the cold
FormList Property VeryWarmClothing  Auto         ; Clothing and armors that provide excellent protection from the cold
FormList Property ExcludedClothing  Auto         ; Clothing and armors that provide no protection from the cold

; Fixed-preset compatibility shim. Do not register this menu with SkyUI.
SKI_ConfigManager _hiddenManager
int _cleanupAttempts = 0

int function GetVersion()
	return 3
endFunction

event OnInit()
	OnGameReload()
endEvent

event OnGameReload()
	GoToState("")
	UnregisterForAllKeys()
	UnregisterForModEvent("SKICP_configManagerReady")
	UnregisterForModEvent("SKICP_configManagerReset")
	RegisterForModEvent("SKICP_configManagerReady", "OnConfigManagerReady")
	RegisterForModEvent("SKICP_configManagerReset", "OnConfigManagerReset")
	_cleanupAttempts = 0
	RegisterForSingleUpdate(1.0)
endEvent

event OnConfigManagerReady(string a_eventName, string a_strArg, float a_numArg, Form a_sender)
	_hiddenManager = a_sender as SKI_ConfigManager
	_cleanupAttempts = 0
	HideOwnMenu()
	RegisterForSingleUpdate(2.0)
endEvent

event OnConfigManagerReset(string a_eventName, string a_strArg, float a_numArg, Form a_sender)
	_hiddenManager = none
endEvent

function HideOwnMenu()
	if (_hiddenManager)
		_hiddenManager.UnregisterMod(self)
	endIf
endFunction

event OnUpdate()
	HideOwnMenu()
	_cleanupAttempts += 1
	if (_cleanupAttempts < 5)
		RegisterForSingleUpdate(2.0)
	endIf
endEvent

event OnConfigOpen()
	GoToState("")
	HideOwnMenu()
endEvent

event OnConfigClose()
	UnregisterForAllKeys()
	GoToState("")
	_cleanupAttempts = 0
	RegisterForSingleUpdate(1.0)
endEvent

event OnVersionUpdate(int version)
endEvent

event OnPageReset(string page)
{An old cached menu can briefly remain until SkyUI accepts unregistration. It has no controls.}
	SetCursorFillMode(TOP_TO_BOTTOM)
	AddHeaderOption("固定预设已锁定")
	AddTextOption("凉爽降温量", "0.0075")
	AddTextOption("寒冷降温量", "0.015")
	AddTextOption("严寒降温量", "0.05")
	AddTextOption("取暖动画", "开启")
	AddTextOption("局内设置", "已关闭")
endEvent

function ResetPageSettings()
endFunction

function ResetPageCompatibility()
endFunction

string function GetClothingWarmthDisplay(Form akWornItem, bool ignoreDetection = false)
	return "固定预设"
endFunction

state ENABLED_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state POLLING_INTERVAL_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state SUNRISE_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state SUNSET_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state HEATSOURCE_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state WARM_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state COMFORTABLE_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state NONE_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state COOL_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state COLD_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state FREEZING_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state FOOD_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state ENABLED_WARMING_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state DETECT_CLOTHING_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state VERBOSE_FEEDBACK_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state HEALTH_DEBUFF_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state STAMINA_DEBUFF_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state MAGICKA_DEBUFF_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state REGEN_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state DAMAGE_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state DAMAGE_DELTA_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state VAMPIRE_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state WEREWOLF_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state LICH_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state WIDGET_SHOWN_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state WIDGET_FADE_TOGGLE
	event OnSelectST()
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state WIDGET_HOTKEY_MAP
	event OnKeyMapChangeST(int newCode, string conflictControl, string conflictName)
	endEvent
	event OnDefaultST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state WIDGET_TOP_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state WIDGET_LEFT_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state WIDGET_WIDTH_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state WIDGET_HEIGHT_SLIDER
	event OnSliderOpenST()
	endEvent
	event OnSliderAcceptST(float value)
	endEvent
	event OnHighlightST()
	endEvent
endState

state ADD_LOCATION_TEXT
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state ADD_CELL_TEXT
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state REMOVE_LOCATION_TEXT
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state REMOVE_CELL_TEXT
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state RESET_HEAD
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state RESET_BODY
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state RESET_HANDS
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state RESET_CLOAK
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state RESET_CLOTHING
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState

state RESET_FOODS
	event OnSelectST()
	endEvent
	event OnHighlightST()
	endEvent
endState
