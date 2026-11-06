Scriptname _M_AliasPlayerGather extends ReferenceAlias  

ReferenceAlias Property ItemRef Auto

GlobalVariable Property ItemCount Auto
GlobalVariable Property ItemTotal Auto

Event OnInit()
	if(ItemRef.GetRef())
		AddInventoryEventFilter(ItemRef.GetRef().GetBaseObject())
	endIf
endEvent

Event OnItemAdded(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akSourceContainer)
    If !STRMissivesBridge.IsPersonalQuest(GetOwningQuest().GetFormID())
        Return
    EndIf
	Form ItemBase = ItemRef.GetRef().GetBaseObject() as Form
	if(GetOwningQuest().GetStage() == 20 && akBaseItem == ItemBase)
		ItemCount.SetValue(GetRef().GetItemCount(ItemBase))
		GetOwningQuest().UpdateCurrentInstanceGlobal(ItemCount)
		if(ItemCount.GetValue() >= ItemTotal.GetValue())
			GetOwningQuest().SetObjectiveCompleted(20)
			GetOwningQuest().SetObjectiveDisplayed(40, true, true)
		endIf
	endIf
endEvent

Event OnItemRemoved(Form akBaseItem, int aiItemCount, ObjectReference akItemReference, ObjectReference akDestContainer)
    If !STRMissivesBridge.IsPersonalQuest(GetOwningQuest().GetFormID())
        Return
    EndIf
	Form ItemBase = ItemRef.GetRef().GetBaseObject() as Form
	if(GetOwningQuest().GetStage() == 20 && akBaseItem == ItemBase)
		ItemCount.SetValue(GetRef().GetITemCount(ItemBase))
		GetOwningQuest().UpdateCurrentInstanceGlobal(ItemCount)
		if(ItemCount.GetValue() < ItemTotal.GetValue() && GetOwningQuest().IsObjectiveDisplayed(40))
			GetOwningQuest().SetObjectiveCompleted(20, false)
			GetOwningQuest().SetObjectiveDisplayed(20, true, true)
			GetOwningQuest().SetObjectiveDisplayed(40, false)
		endIf
	endIf
endEvent