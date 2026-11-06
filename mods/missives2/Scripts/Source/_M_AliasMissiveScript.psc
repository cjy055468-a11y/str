Scriptname _M_AliasMissiveScript extends ReferenceAlias  

Message Property _M_MessageDiscard Auto

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
    STRHolder = akNewContainer
    If akNewContainer == Game.GetPlayer() && GetOwningQuest().GetStage() < 20
        If STRMissivesBridge.IsConnected() && !STRMissivesBridge.IsPersonalQuest(GetOwningQuest().GetFormID())
            STRMissivesBridge.Claim(GetOwningQuest().GetFormID())
            RegisterForSingleUpdate(0.1)
        Else
            GetOwningQuest().SetStage(20)
        EndIf
    EndIf
EndEvent

Event OnUpdate()
    STRMissivesBridge.RefreshPosting(GetOwningQuest())
    If STRMissivesBridge.IsConnected() && STRMissivesBridge.GetState(GetOwningQuest().GetFormID()) == 1
        RegisterForSingleUpdate(0.1)
    EndIf
EndEvent

Event OnEquipped(Actor akActor)
    If !STRMissivesBridge.IsPersonalQuest(GetOwningQuest().GetFormID())
        Return
    EndIf
	if(akActor == Game.GetPlayer() && GetOwningQuest().GetStage() > 0)
		Utility.WaitMenuMode(2)
		if(_M_MessageDiscard.Show() == 0)
			Utility.Wait(0.01)
			GetOwningQuest().SetStage(105)
		endIf
	endIf
endEvent
ObjectReference STRHolder
ObjectReference Function STRGetHolder()
    Return STRHolder
EndFunction
