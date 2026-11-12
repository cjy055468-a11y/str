Scriptname _M_AliasMissiveScript extends ReferenceAlias
Message Property _M_MessageDiscard Auto

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
    Quest mission = GetOwningQuest()
    If akNewContainer == Game.GetPlayer() && mission.GetStage() < 20
        If !STRNoticeBridge.IsConnected() || STRNoticeBridge.IsLocalTask(mission.GetFormID())
            mission.SetStage(20)
        EndIf
    EndIf
EndEvent

Event OnEquipped(Actor akActor)
    Quest mission = GetOwningQuest()
    If STRNoticeBridge.IsConnected() && !STRNoticeBridge.IsLocalTask(mission.GetFormID())
        Return
    EndIf
    If akActor == Game.GetPlayer() && mission.GetStage() > 0
        Utility.WaitMenuMode(2)
        If _M_MessageDiscard.Show() == 0
            Utility.Wait(0.01)
            mission.SetStage(105)
        EndIf
    EndIf
EndEvent
