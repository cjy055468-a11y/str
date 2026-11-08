Scriptname _M_AliasPlayerCourier extends ReferenceAlias

GlobalVariable Property DeliveryDate Auto
GlobalVariable Property GameDaysPassed Auto

Event OnInit()
	RegisterForUpdateGameTime(6.0)
endEvent

Event OnUpdateGameTime()
	if(GetOwningQuest().GetStage() > 20)
		if(GameDaysPassed.GetValue() > DeliveryDate.GetValue())
			GetOwningQuest().SetStage(103)
		endIf
	endIf
endEvent