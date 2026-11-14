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

event OnGameReload()
	RepairLocalBindings()
	parent.OnGameReload()
endEvent

event OnConfigOpen()
	RepairLocalBindings()
endEvent

function RepairLocalBindings()
{Recover the two references that the old binary-only translation could leave empty.}
	if (!Widget)
		Widget = self as _JSW_FB_MeterWidget
	endIf
	if (!Enabled)
		_JSW_FB_HandlerScript handler = GetAlias(0) as _JSW_FB_HandlerScript
		if (handler)
			Enabled = handler.Enabled
		endIf
	endIf
endFunction

int function GetVersion()
	return 2
endFunction

event OnVersionUpdate(int version)
	if (version >= 2)
		Pages = new String[2]
		Pages[0] = "设置"
		Pages[1] = "兼容性"
	endIf
endEvent

event OnConfigClose()
	UnregisterForAllKeys()
	RegisterForKey(WidgetHotKey.GetValueInt())
endEvent

event OnPageReset(string page)
	if (page == "")
		UnloadCustomContent()
		ResetPageSettings()
	else
		UnloadCustomContent()
		
		if (page == "设置")
			ResetPageSettings()
		elseIf (page == "兼容性")
			ResetPageCompatibility()
		endIf
	endIf
endEvent

function ResetPageSettings()
	SetCursorFillMode(TOP_TO_BOTTOM)
	
	AddToggleOptionST("ENABLED_TOGGLE", "启用体温系统", Enabled.GetValueInt())
	AddSliderOptionST("POLLING_INTERVAL_SLIDER", "检测间隔", PollingInterval.GetValue(), "{0}s")
	
	AddHeaderOption("环境")
	AddSliderOptionST("SUNRISE_SLIDER", "日出时间", Sunrise.GetValue(), "{1}")
	AddSliderOptionST("SUNSET_SLIDER", "日落时间", Sunset.GetValue(), "{1}")
	AddSliderOptionST("HEATSOURCE_SLIDER", "热源范围", HeatSourceRadius.GetValue(), "{1} 单位")
	
	AddHeaderOption("体温变化")
	AddSliderOptionST("WARM_DELTA_SLIDER", "温暖环境回温量", WarmDelta.GetValue(), "{4}")
	AddSliderOptionST("COMFORTABLE_DELTA_SLIDER", "舒适环境回温量", ComfortableDelta.GetValue(), "{4}")
	AddSliderOptionST("NONE_DELTA_SLIDER", "中性环境回温量", NoneDelta.GetValue(), "{4}")
	AddSliderOptionST("COOL_DELTA_SLIDER", "凉爽环境降温量", CoolDelta.GetValue(), "{4}")
	AddSliderOptionST("COLD_DELTA_SLIDER", "寒冷环境降温量", ColdDelta.GetValue(), "{4}")
	AddSliderOptionST("FREEZING_DELTA_SLIDER", "严寒环境降温量", FreezingDelta.GetValue(), "{4}")
	AddSliderOptionST("FOOD_DELTA_SLIDER", "食物回温量", FoodDelta.GetValue(), "{4}")
	
	AddHeaderOption("其他设置")
	AddToggleOptionST("ENABLED_WARMING_TOGGLE", "取暖动作", WarmingAnimation.GetValueInt())
	AddToggleOptionST("DETECT_CLOTHING_TOGGLE", "自动识别衣物", DetectClothing.GetValueInt())
	AddToggleOptionST("WIDGET_FADE_TOGGLE", "体温条自动淡出", WidgetFade.GetValueInt())
	AddToggleOptionST("VERBOSE_FEEDBACK_TOGGLE", "状态提示", VerboseFeedback.GetValueInt())
	
	SetCursorPosition(1)
	
	AddHeaderOption("低温惩罚")
	AddToggleOptionST("HEALTH_DEBUFF_TOGGLE", "生命", HealthDebuff.GetValueInt())
	AddToggleOptionST("STAMINA_DEBUFF_TOGGLE", "耐力", StaminaDebuff.GetValueInt())
	AddToggleOptionST("MAGICKA_DEBUFF_TOGGLE", "魔法", MagickaDebuff.GetValueInt())
	AddSliderOptionST("REGEN_SLIDER", "停止恢复的体温阈值", RegenDebuff.GetValue(), "{1}")
	AddSliderOptionST("DAMAGE_SLIDER", "开始扣值的体温阈值", DamageDebuff.GetValue(), "{1}")
	AddSliderOptionST("DAMAGE_DELTA_SLIDER", "每次扣除比例", DamageDelta.GetValue(), "{0}%")
	
	AddHeaderOption("特殊种族")
	AddToggleOptionST("VAMPIRE_TOGGLE", "吸血鬼免疫低温", EnableVampires.GetValueInt())
	AddToggleOptionST("WEREWOLF_TOGGLE", "狼人形态免疫低温", EnableWerewolves.GetValueInt())
	AddToggleOptionST("LICH_TOGGLE", "巫妖免疫低温", EnableLiches.GetValueInt())
	
	AddHeaderOption("体温条")
	AddToggleOptionST("WIDGET_SHOWN_TOGGLE", "显示体温条", WidgetShown.GetValueInt())
	AddKeyMapOptionST("WIDGET_HOTKEY_MAP", "显示切换快捷键", WidgetHotKey.GetValueInt())
	AddSliderOptionST("WIDGET_TOP_SLIDER", "垂直位置", WidgetTop.GetValueInt(), "{0}px")
	AddSliderOptionST("WIDGET_LEFT_SLIDER", "水平位置", WidgetLeft.GetValueInt(), "{0}px")
	AddSliderOptionST("WIDGET_WIDTH_SLIDER", "体温条宽度", WidgetWidth.GetValueInt(), "{0}px")
	AddSliderOptionST("WIDGET_HEIGHT_SLIDER", "体温条高度", WidgetHeight.GetValueInt(), "{0}px")
endFunction

function ResetPageCompatibility()
	SetCursorFillMode(TOP_TO_BOTTOM)
	
	if (!PlayerRef.IsInInterior())
		AddHeaderOption("当前位于室外")
	else
		Location currLoc = PlayerRef.GetCurrentLocation()
		Cell currCell = PlayerRef.GetParentCell()
		
		AddHeaderOption("当前室内区域")
		AddTextOption("地点：" + currLoc.GetName(), "")
		
		if (InteriorColdZones.HasForm(currLoc))
			AddTextOption("\t已标记为寒冷区域", "")
		else
			AddTextOption("\t未标记为寒冷区域", "")
		endIf
		
		AddTextOption("单元格：" + currCell.GetFormID(), "")
		
		if (InteriorColdZones.HasForm(currCell))
			AddTextOption("\t已标记为寒冷区域", "")
		else
			AddTextOption("\t未标记为寒冷区域", "")
		endIf
		
		AddEmptyOption()
		
		AddTextOptionST("ADD_LOCATION_TEXT", "添加寒冷地点：" + currLoc.GetName(), "")
		AddTextOptionST("ADD_CELL_TEXT", "添加寒冷单元格：" + currCell.GetFormID(), "")
		AddTextOptionST("REMOVE_LOCATION_TEXT", "移除寒冷地点：" + currLoc.GetName(), "")
		AddTextOptionST("REMOVE_CELL_TEXT", "移除寒冷单元格：" + currCell.GetFormID(), "")
	endIf
	
	SetCursorPosition(1)
	
	AddHeaderOption("衣物保暖")
	
	Armor headClothing = PlayerRef.GetWornForm(0x00000002) as Armor
	Armor bodyClothing = PlayerRef.GetWornForm(0x00000004) as Armor
	Armor handsClothing = PlayerRef.GetWornForm(0x00000008) as Armor
	Armor cloakClothing = PlayerRef.GetWornForm(0x00010000) as Armor
	
	if (headClothing && (headClothing.HasKeywordString("ClothingHead") || headClothing.HasKeywordString("ArmorHelmet")))
		AddTextOption("头部：" + headClothing.GetName(), "")
		AddTextOption("\t" + GetClothingWarmthDisplay(headClothing), "")
	else
		AddTextOption("头部：" + "未穿戴", "")
	endIf
	
	if (bodyClothing)
		AddTextOption("身体：" + bodyClothing.GetName(), "")
		AddTextOption("\t" + GetClothingWarmthDisplay(bodyClothing), "")
	else
		AddTextOption("身体：" + "未穿戴", "")
	endIf
	
	if (handsClothing)
		AddTextOption("手部：" + handsClothing.GetName(), "")
		AddTextOption("\t" + GetClothingWarmthDisplay(handsClothing), "")
	else
		AddTextOption("手部：" + "未穿戴", "")
	endIf
	
	if (cloakClothing)
		AddTextOption("披风：" + cloakClothing.GetName(), "")
		AddTextOption("\t" + GetClothingWarmthDisplay(cloakClothing, true), "")
	else
		AddTextOption("披风：" + "未穿戴", "")
	endIf
	
	if (DetectClothing.GetValueInt())
		AddEmptyOption()
		
		if (headClothing && (headClothing.HasKeywordString("ClothingHead") || headClothing.HasKeywordString("ArmorHelmet")))
			AddTextOptionST("RESET_HEAD", "重置当前头部装备", "")
		endIf
		
		if (bodyClothing)
			AddTextOptionST("RESET_BODY", "重置当前身体装备", "")
		endIf
		
		if (handsClothing)
			AddTextOptionST("RESET_HANDS", "重置当前手部装备", "")
		endIf
	endIf
	
	if (cloakClothing)
		AddTextOptionST("RESET_CLOAK", "重置当前披风", "")
	endIf
	
	AddTextOptionST("RESET_CLOTHING", "重置全部衣物记录", "")
	
	AddEmptyOption()
	
	AddHeaderOption("暖身食物")
	AddTextOptionST("RESET_FOODS", "重置全部食物记录", "")
endFunction

string function GetClothingWarmthDisplay(Armor akWornItem, bool ignoreDetection = false)
{Identify the warmth display string for the given item}
	string warmthDisplay = "尚未设置保暖等级"
	
	if (!ignoreDetection && DetectClothing.GetValueInt())
		if (akWornItem.HasKeywordString("ArmorHeavy"))
			warmthDisplay = "保暖效果极佳"
		elseIf (akWornItem.HasKeywordString("ArmorLight"))
			warmthDisplay = "提供一定保暖"
		elseIf (akWornItem.HasKeywordString("ArmorClothing"))
			warmthDisplay = "几乎不保暖"
		endIf
	else
		if (VeryWarmClothing.HasForm(akWornItem))
			warmthDisplay = "保暖效果极佳"
		elseIf (WarmClothing.HasForm(akWornItem))
			warmthDisplay = "提供一定保暖"
		elseIf (ExcludedClothing.HasForm(akWornItem))
			warmthDisplay = "几乎不保暖"
		endIf
	endIf
	
	return warmthDisplay
endFunction

state ENABLED_TOGGLE
	event OnSelectST()
		if (Enabled.GetValueInt())
			Enabled.SetValueInt(0)
			WidgetShown.SetValueInt(0)
			Widget.Alpha = 0.0
		else
			Enabled.SetValueInt(1)
			WidgetShown.SetValueInt(1)
			Widget.Alpha = 100.0
		endIf
		
		SetToggleOptionValueST(Enabled.GetValueInt())
		SendModEvent("FrostbiteWidgetReset")
		ForcePageReset()
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(Enabled.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("启用或停用体温系统。停用时会清除低温恢复惩罚并停止取暖动作。")
	endEvent
endState

state POLLING_INTERVAL_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(PollingInterval.GetValue())
		SetSliderDialogRange(1, 60)
		SetSliderDialogInterval(1)
	endEvent

	event OnSliderAcceptST(float value)
		PollingInterval.SetValue(value)
		SetSliderOptionValueST(value, "{0}s")
	endEvent

	event OnHighlightST()
		SetInfoText("每隔多少现实秒检测一次体温。默认每 5 秒检测一次。")
	endEvent
endState

state SUNRISE_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(Sunrise.GetValue())
		SetSliderDialogRange(1, 24)
		SetSliderDialogInterval(1)
	endEvent

	event OnSliderAcceptST(float value)
		Sunrise.SetValue(value)
		SetSliderOptionValueST(value, "{0}")
	endEvent

	event OnHighlightST()
		SetInfoText("以 24 小时制设置日出时间。\n晴天从这一时间开始获得日照带来的温暖。")
	endEvent
endState

state SUNSET_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(Sunset.GetValue())
		SetSliderDialogRange(1, 24)
		SetSliderDialogInterval(1)
	endEvent

	event OnSliderAcceptST(float value)
		Sunset.SetValue(value)
		SetSliderOptionValueST(value, "{0}")
	endEvent

	event OnHighlightST()
		SetInfoText("以 24 小时制设置日落时间。\n日落后环境会变冷。")
	endEvent
endState

state HEATSOURCE_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(HeatSourceRadius.GetValue())
		SetSliderDialogRange(64, 1024)
		SetSliderDialogInterval(1)
	endEvent

	event OnSliderAcceptST(float value)
		HeatSourceRadius.SetValue(value)
		SetSliderOptionValueST(value, "{0} 单位")
	endEvent

	event OnHighlightST()
		SetInfoText("热源周围可以取暖的距离，单位为游戏距离。")
	endEvent
endState

state WARM_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(WarmDelta.GetValue())
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.0001)
	endEvent

	event OnSliderAcceptST(float value)
		WarmDelta.SetValue(value)
		SetSliderOptionValueST(value, "{4}")
	endEvent

	event OnHighlightST()
		SetInfoText("温暖环境中，每次检测恢复的体温量。\n体温条显示为红色。")
	endEvent
endState

state COMFORTABLE_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(ComfortableDelta.GetValue())
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.0001)
	endEvent

	event OnSliderAcceptST(float value)
		ComfortableDelta.SetValue(value)
		SetSliderOptionValueST(value, "{4}")
	endEvent

	event OnHighlightST()
		SetInfoText("舒适环境中，每次检测恢复的体温量。\n体温条显示为浅红色。")
	endEvent
endState

state NONE_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(NoneDelta.GetValue())
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.0001)
	endEvent

	event OnSliderAcceptST(float value)
		NoneDelta.SetValue(value)
		SetSliderOptionValueST(value, "{4}")
	endEvent

	event OnHighlightST()
		SetInfoText("不冷不热的环境中，每次检测恢复的体温量。\n体温条显示为白色。")
	endEvent
endState

state COOL_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(CoolDelta.GetValue())
		SetSliderDialogDefaultValue(0.0075)
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.0001)
	endEvent

	event OnSliderAcceptST(float value)
		CoolDelta.SetValue(value)
		SetSliderOptionValueST(value, "{4}")
	endEvent

	event OnHighlightST()
		SetInfoText("凉爽环境中，每次检测损失的体温量。\n默认 0.0075，为原版的 1.5 倍；体温条显示为浅蓝色。")
	endEvent

	event OnDefaultST()
		CoolDelta.SetValue(0.0075)
		SetSliderOptionValueST(0.0075, "{4}")
	endEvent
endState

state COLD_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(ColdDelta.GetValue())
		SetSliderDialogDefaultValue(0.015)
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.0001)
	endEvent

	event OnSliderAcceptST(float value)
		ColdDelta.SetValue(value)
		SetSliderOptionValueST(value, "{4}")
	endEvent

	event OnHighlightST()
		SetInfoText("寒冷环境中，每次检测损失的体温量。\n默认 0.015，为原版的 1.5 倍；体温条显示为蓝色。")
	endEvent

	event OnDefaultST()
		ColdDelta.SetValue(0.015)
		SetSliderOptionValueST(0.015, "{4}")
	endEvent
endState

state FREEZING_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(FreezingDelta.GetValue())
		SetSliderDialogDefaultValue(0.0375)
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.0001)
	endEvent

	event OnSliderAcceptST(float value)
		FreezingDelta.SetValue(value)
		SetSliderOptionValueST(value, "{4}")
	endEvent

	event OnHighlightST()
		SetInfoText("严寒环境中，每次检测损失的体温量。\n默认 0.0375，为原版的 1.5 倍；体温条显示为粉色。")
	endEvent

	event OnDefaultST()
		FreezingDelta.SetValue(0.0375)
		SetSliderOptionValueST(0.0375, "{4}")
	endEvent
endState

state FOOD_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(FoodDelta.GetValue())
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.0001)
	endEvent

	event OnSliderAcceptST(float value)
		FoodDelta.SetValue(value)
		SetSliderOptionValueST(value, "{4}")
	endEvent

	event OnHighlightST()
		SetInfoText("食用暖身食物时立即恢复的体温量。")
	endEvent
endState

state ENABLED_WARMING_TOGGLE
	event OnSelectST()
		if (WarmingAnimation.GetValueInt())
			WarmingAnimation.SetValueInt(0)
		else
			WarmingAnimation.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(WarmingAnimation.GetValueInt())
		SendModEvent("FrostbiteWidgetReset")
		ForcePageReset()
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(WarmingAnimation.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("靠近热源时播放取暖动作。移动、交互、拔出武器、跳跃或潜行会停止动作。")
	endEvent
endState

state DETECT_CLOTHING_TOGGLE
	event OnSelectST()
		if (DetectClothing.GetValueInt())
			DetectClothing.SetValueInt(0)
		else
			DetectClothing.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(DetectClothing.GetValueInt())
		ForcePageReset()
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(DetectClothing.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("按衣物类型自动判断保暖程度。关闭后，可手动记录衣物的保暖等级。")
	endEvent
endState

state VERBOSE_FEEDBACK_TOGGLE
	event OnSelectST()
		if (VerboseFeedback.GetValueInt())
			VerboseFeedback.SetValueInt(0)
		else
			VerboseFeedback.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(VerboseFeedback.GetValueInt())
		ForcePageReset()
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(VerboseFeedback.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("显示额外的体温状态提示。\n进入寒冷区域或完全暖和时播放画面效果，并显示当前环境提示。")
	endEvent
endState

state HEALTH_DEBUFF_TOGGLE
	event OnSelectST()
		if (HealthDebuff.GetValueInt())
			HealthDebuff.SetValueInt(0)
		else
			HealthDebuff.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(HealthDebuff.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(HealthDebuff.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("体温过低时施加生命惩罚。\n达到恢复阈值后停止自然恢复；达到扣值阈值后开始扣除生命。默认关闭。")
	endEvent
endState

state STAMINA_DEBUFF_TOGGLE
	event OnSelectST()
		if (StaminaDebuff.GetValueInt())
			StaminaDebuff.SetValueInt(0)
		else
			StaminaDebuff.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(StaminaDebuff.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(StaminaDebuff.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("体温过低时施加耐力惩罚。\n达到恢复阈值后停止自然恢复；达到扣值阈值后开始扣除耐力。")
	endEvent
endState

state MAGICKA_DEBUFF_TOGGLE
	event OnSelectST()
		if (MagickaDebuff.GetValueInt())
			MagickaDebuff.SetValueInt(0)
		else
			MagickaDebuff.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(MagickaDebuff.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(MagickaDebuff.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("体温过低时施加魔法惩罚。\n达到恢复阈值后停止自然恢复；达到扣值阈值后开始扣除魔法。")
	endEvent
endState

state REGEN_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(RegenDebuff.GetValue())
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.1)
	endEvent

	event OnSliderAcceptST(float value)
		RegenDebuff.SetValue(value)
		SetSliderOptionValueST(value, "{1}")
	endEvent

	event OnHighlightST()
		SetInfoText("体温降至该值及以下时，停止已启用属性的自然恢复。体温范围为 0 至 1。")
	endEvent
endState

state DAMAGE_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(DamageDebuff.GetValue())
		SetSliderDialogRange(0.0, 1.0)
		SetSliderDialogInterval(0.1)
	endEvent

	event OnSliderAcceptST(float value)
		DamageDebuff.SetValue(value)
		SetSliderOptionValueST(value, "{1}")
	endEvent

	event OnHighlightST()
		SetInfoText("体温降至该值及以下时，每次检测都会扣除已启用的属性。体温范围为 0 至 1。")
	endEvent
endState

state DAMAGE_DELTA_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(DamageDelta.GetValue())
		SetSliderDialogRange(1.0, 100.0)
		SetSliderDialogInterval(1.0)
	endEvent

	event OnSliderAcceptST(float value)
		DamageDelta.SetValue(value)
		SetSliderOptionValueST(value, "{0}%")
	endEvent

	event OnHighlightST()
		SetInfoText("每次检测按基础属性值的这一比例扣值。冰抗会降低扣除量，100% 冰抗可完全抵消；负冰抗会增加扣除量。")
	endEvent
endState

state VAMPIRE_TOGGLE
	event OnSelectST()
		if (EnableVampires.GetValueInt())
			EnableVampires.SetValueInt(0)
		else
			EnableVampires.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(EnableVampires.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(EnableVampires.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("吸血鬼不再因环境寒冷而继续降温。")
	endEvent
endState

state WEREWOLF_TOGGLE
	event OnSelectST()
		if (EnableWerewolves.GetValueInt())
			EnableWerewolves.SetValueInt(0)
		else
			EnableWerewolves.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(EnableWerewolves.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(EnableWerewolves.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("变身后的狼人不再因环境寒冷而继续降温。")
	endEvent
endState

state LICH_TOGGLE
	event OnSelectST()
		if (EnableLiches.GetValueInt())
			EnableLiches.SetValueInt(0)
		else
			EnableLiches.SetValueInt(1)
		endIf
		
		SetToggleOptionValueST(EnableLiches.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(EnableLiches.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("巫妖形态不再因环境寒冷而继续降温，包括受支持模组提供的巫妖形态。")
	endEvent
endState

state WIDGET_SHOWN_TOGGLE
	event OnSelectST()
		if (WidgetShown.GetValueInt())
			WidgetShown.SetValueInt(0)
		else
			WidgetShown.SetValueInt(1)
		endIf
		
		SendModEvent("FrostbiteWidgetReset")
		SetToggleOptionValueST(WidgetShown.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(WidgetShown.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("显示或隐藏体温条。")
	endEvent
endState

state WIDGET_FADE_TOGGLE
	event OnSelectST()
		if (WidgetFade.GetValueInt())
			WidgetFade.SetValueInt(0)
		else
			WidgetFade.SetValueInt(1)
		endIf
		
		SendModEvent("FrostbiteWidgetReset")
		SetToggleOptionValueST(WidgetFade.GetValueInt())
	endEvent

	event OnDefaultST()
		SetToggleOptionValueST(WidgetFade.GetValueInt())
	endEvent

	event OnHighlightST()
		SetInfoText("完全暖和后，体温条会自动淡出。再次降温时恢复显示。")
	endEvent
endState

state WIDGET_HOTKEY_MAP
	event OnKeyMapChangeST(int newCode, string conflictControl, string conflictName)
		bool doMap = true
		
		if (conflictControl != "")
			doMap = ShowMessage("该按键已绑定到“" + conflictControl + "”。是否继续？")
		endIf
		
		if (doMap)
			WidgetHotKey.SetValueInt(newCode)
			SetKeyMapOptionValueST(WidgetHotKey.GetValueInt())
		endIf
	endEvent
	
	event OnDefaultST()
		WidgetHotKey.SetValueInt(10)
		SetKeyMapOptionValueST(WidgetHotKey.GetValueInt())
	endEvent
	
	event OnHighlightST()
		SetInfoText("设置显示或隐藏体温条的快捷键，默认为数字键 9。")
	endEvent
endState

state WIDGET_TOP_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(WidgetTop.GetValueInt())
		SetSliderDialogRange(0.0, 4320.0) ; 8K UHD overkill?
		SetSliderDialogInterval(1)
	endEvent
	
	event OnSliderAcceptST(float value)
		WidgetTop.SetValueInt(value as int)
		SendModEvent("FrostbiteWidgetReset")
		SetSliderOptionValueST(value as int, "{0}px")
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("体温条距画面顶部的位置，单位为像素。")
	endEvent
endState

state WIDGET_LEFT_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(WidgetLeft.GetValueInt())
		SetSliderDialogRange(0.0, 7680.0) ; 8K UHD overkill?
		SetSliderDialogInterval(1)
	endEvent
	
	event OnSliderAcceptST(float value)
		WidgetLeft.SetValueInt(value as int)
		SendModEvent("FrostbiteWidgetReset")
		SetSliderOptionValueST(value as int, "{0}px")
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("体温条距画面左侧的位置，单位为像素。")
	endEvent
endState

state WIDGET_WIDTH_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(WidgetWidth.GetValue())
		SetSliderDialogRange(0.0, 7680.0) ; 8K UHD overkill?
		SetSliderDialogInterval(1.0)
	endEvent

	event OnSliderAcceptST(float value)
		WidgetWidth.SetValue(value)
		SetSliderOptionValueST(value, "{0}px")
		SendModEvent("FrostbiteWidgetReset")
	endEvent

	event OnHighlightST()
		SetInfoText("体温条的宽度，单位为像素。")
	endEvent
endState

state WIDGET_HEIGHT_SLIDER
	event OnSliderOpenST()
		SetSliderDialogStartValue(WidgetHeight.GetValue())
		SetSliderDialogRange(0.0, 4320.0) ; 8K UHD overkill?
		SetSliderDialogInterval(1.0)
	endEvent

	event OnSliderAcceptST(float value)
		WidgetHeight.SetValue(value)
		SetSliderOptionValueST(value, "{0}px")
		SendModEvent("FrostbiteWidgetReset")
	endEvent

	event OnHighlightST()
		SetInfoText("体温条的高度，单位为像素。")
	endEvent
endState

state ADD_LOCATION_TEXT
	event OnSelectST()
		Location currLoc = PlayerRef.GetCurrentLocation()
		
		if (!InteriorColdZones.HasForm(currLoc))
			InteriorColdZones.AddForm(currLoc)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("将当前地点标记为寒冷区域。")
	endEvent
endState

state ADD_CELL_TEXT
	event OnSelectST()
		Cell currCell = PlayerRef.GetParentCell()
		
		if (!InteriorColdCells.HasForm(currCell))
			InteriorColdCells.AddForm(currCell)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("将当前单元格标记为寒冷区域。")
	endEvent
endState

state REMOVE_LOCATION_TEXT
	event OnSelectST()
		Location currLoc = PlayerRef.GetCurrentLocation()
		
		if (InteriorColdZones.HasForm(currLoc))
			InteriorColdZones.RemoveAddedForm(currLoc)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("移除当前地点的寒冷标记。\n只能移除通过 MCM 手动添加的记录。")
	endEvent
endState

state REMOVE_CELL_TEXT
	event OnSelectST()
		Cell currCell = PlayerRef.GetParentCell()
		
		if (InteriorColdCells.HasForm(currCell))
			InteriorColdCells.RemoveAddedForm(currCell)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("移除当前单元格的寒冷标记。\n只能移除通过 MCM 手动添加的记录。")
	endEvent
endState

state RESET_HEAD
	event OnSelectST()
		Armor head = PlayerRef.GetWornForm(0x00000002) as Armor
		
		if (WarmClothing.HasForm(head))
			WarmClothing.RemoveAddedForm(head)
		endIf
		
		if (VeryWarmClothing.HasForm(head))
			VeryWarmClothing.RemoveAddedForm(head)
		endIf
		
		if (ExcludedClothing.HasForm(head))
			ExcludedClothing.RemoveAddedForm(head)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("重置当前头部装备（槽位 30）的手动保暖记录。")
	endEvent
endState

state RESET_BODY
	event OnSelectST()
		Armor body = PlayerRef.GetWornForm(0x00000004) as Armor
		
		if (WarmClothing.HasForm(body))
			WarmClothing.RemoveAddedForm(body)
		endIf
		
		if (VeryWarmClothing.HasForm(body))
			VeryWarmClothing.RemoveAddedForm(body)
		endIf
		
		if (ExcludedClothing.HasForm(body))
			ExcludedClothing.RemoveAddedForm(body)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("重置当前身体装备（槽位 32）的手动保暖记录。")
	endEvent
endState

state RESET_HANDS
	event OnSelectST()
		Armor hands = PlayerRef.GetWornForm(0x00000008) as Armor
		
		if (WarmClothing.HasForm(hands))
			WarmClothing.RemoveAddedForm(hands)
		endIf
		
		if (VeryWarmClothing.HasForm(hands))
			VeryWarmClothing.RemoveAddedForm(hands)
		endIf
		
		if (ExcludedClothing.HasForm(hands))
			ExcludedClothing.RemoveAddedForm(hands)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("重置当前手部装备（槽位 33）的手动保暖记录。")
	endEvent
endState

state RESET_CLOAK
	event OnSelectST()
		Armor cloak = PlayerRef.GetWornForm(0x00010000) as Armor
		
		if (WarmClothing.HasForm(cloak))
			WarmClothing.RemoveAddedForm(cloak)
		endIf
		
		if (VeryWarmClothing.HasForm(cloak))
			VeryWarmClothing.RemoveAddedForm(cloak)
		endIf
		
		if (ExcludedClothing.HasForm(cloak))
			ExcludedClothing.RemoveAddedForm(cloak)
		endIf
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("重置当前披风（槽位 46）的手动保暖记录。")
	endEvent
endState

state RESET_CLOTHING
	event OnSelectST()
		WarmClothing.Revert()
		VeryWarmClothing.Revert()
		ExcludedClothing.Revert()
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("清除全部手动添加的衣物保暖记录。")
	endEvent
endState

state RESET_FOODS
	event OnSelectST()
		WarmingFoods.Revert()
		ExcludedFoods.Revert()
		
		ForcePageReset()
	endEvent
	
	event OnHighlightST()
		SetInfoText("清除全部手动添加的食物记录。")
	endEvent
endState