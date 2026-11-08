Scriptname _M_AliasMissiveDeliverScript extends ReferenceAlias

Message Property _M_MessageDiscard Auto

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
    Quest mission = GetOwningQuest()
    If akNewContainer == Game.GetPlayer() && mission.GetStage() < 20
        If STRMissivesBoardBridge.IsConnected() && !STRMissivesBoardBridge.IsPersonalQuest(mission.GetFormID())
            ObjectReference board = akOldContainer
            If !board
                Int boardAliasId = STRMissivesBoardBridge.GetBoardAlias(mission.GetFormID())
                If boardAliasId >= 0
                    ReferenceAlias boardAlias = mission.GetAlias(boardAliasId) as ReferenceAlias
                    If boardAlias
                        board = boardAlias.GetReference()
                    EndIf
                EndIf
            EndIf
            If board
                STRMissivesBoardBridge.Claim(mission.GetFormID(), board.GetFormID())
                RegisterForSingleUpdate(0.1)
            EndIf
        Else
            mission.SetStage(20)
        EndIf
    EndIf
EndEvent

Event OnUpdate()
    Quest mission = GetOwningQuest()
    If !STRMissivesBoardBridge.IsConnected()
        If mission.GetStage() < 20 && Game.GetPlayer().GetItemCount(GetReference()) > 0
            mission.SetStage(20)
        EndIf
        Return
    EndIf
    Int boardAliasId = STRMissivesBoardBridge.GetBoardAlias(mission.GetFormID())
    If boardAliasId < 0
        Return
    EndIf
    ReferenceAlias boardAlias = mission.GetAlias(boardAliasId) as ReferenceAlias
    If !boardAlias
        Return
    EndIf
    ObjectReference board = boardAlias.GetReference()
    If board
        STRMissivesBoardBridge.RefreshPosting(mission, board)
        If mission.GetStage() < 20 && Game.GetPlayer().GetItemCount(GetReference()) > 0
            If STRMissivesBoardBridge.GetPostingStatus(mission.GetFormID(), board.GetFormID()) == 0
                RegisterForSingleUpdate(0.1)
            EndIf
        EndIf
    EndIf
EndEvent

Event OnEquipped(Actor akActor)
    If STRMissivesBoardBridge.IsConnected() && !STRMissivesBoardBridge.IsPersonalQuest(GetOwningQuest().GetFormID())
        Return
    EndIf
    If akActor == Game.GetPlayer() && GetOwningQuest().GetStage() > 0
        Utility.WaitMenuMode(2)
        If _M_MessageDiscard.Show() == 0
            Utility.Wait(0.01)
            If GetOwningQuest().GetStage() == 20
                GetOwningQuest().SetStage(105)
            Else
                GetOwningQuest().SetStage(103)
            EndIf
        EndIf
    EndIf
EndEvent
