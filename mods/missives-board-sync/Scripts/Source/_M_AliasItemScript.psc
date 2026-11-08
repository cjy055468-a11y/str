Scriptname _M_AliasItemScript extends ReferenceAlias

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
	if(GetOwningQuest().GetStage() > 0)
		if(akNewContainer == Game.GetPlayer())
			GetOwningQuest().CompleteAllObjectives()
			GetOwningQuest().SetObjectiveDisplayed(40, true, true)
		elseif(akOldContainer == Game.GetPlayer())
			GetOwningQuest().SetObjectiveDisplayed(40, false)
			GetOwningQuest().SetObjectiveDisplayed(20, true, true)
		endIf
	endIf
endEvent