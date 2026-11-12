Scriptname _M_AliasDeliveryScript extends ReferenceAlias

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
	if(GetOwningQuest().GetStage() > 20)
		if(akNewContainer == Game.GetPlayer())
			GetOwningQuest().SetObjectiveCompleted(30)
			GetOwningQuest().SetObjectiveDisplayed(40, true, true)
		elseif(akOldContainer == Game.GetPlayer())
			GetOwningQuest().SetObjectiveDisplayed(40, false)
			GetOwningQuest().SetObjectiveDisplayed(30, true, true)
		endIf
	endIf
endEvent
