Scriptname _M_ActivatorScript extends ObjectReference

GlobalVariable Property QuestChanceLow Auto
GlobalVariable Property QuestChanceMed Auto
GlobalVariable Property QuestChanceHigh Auto
GlobalVariable Property QuestChanceVeryHigh Auto
FormList Property QuestsLow Auto
FormList Property QuestsMed Auto
FormList Property QuestsHigh Auto
FormList Property QuestsVeryHigh Auto
GlobalVariable Property GameDaysPassed Auto
GlobalVariable Property RefreshRate Auto
ObjectReference Property MissiveBoard Auto

Float LastUpdate = -100.0
Bool STRInside = False
Bool STRWasConnected = False
Bool STRRegistered = False
Bool STRBootstrapped = False

Event OnInit()
    RegisterForSingleUpdate(1.0)
EndEvent

Event OnLoad()
    STRRegistered = False
    RegisterForSingleUpdate(0.2)
EndEvent

Event OnCellAttach()
    RegisterForSingleUpdate(0.2)
EndEvent

Event OnCellDetach()
    If STRRegistered && STRMissivesBridge.IsConnected()
        STRMissivesBridge.CloseBoard(MissiveBoard.GetFormID())
    EndIf
    STRRegistered = False
    STRInside = False
    UnregisterForUpdate()
EndEvent

Event OnTriggerEnter(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        STRInside = True
        If STRMissivesBridge.IsConnected()
            STRMissivesBridge.OpenBoard(MissiveBoard.GetFormID(), GetFormID())
            STRRegistered = True
        Else
            STRUpdateBoard(False)
        EndIf
        RegisterForSingleUpdate(0.2)
    EndIf
EndEvent

Event OnTriggerLeave(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        STRInside = False
        If STRRegistered && STRMissivesBridge.IsConnected()
            STRMissivesBridge.CloseBoard(MissiveBoard.GetFormID())
        EndIf
        STRRegistered = False
    EndIf
EndEvent

Event OnUpdate()
    Bool online = STRMissivesBridge.IsConnected()
    If online && !STRWasConnected
        STRRegistered = False
        STRBootstrapped = False
    ElseIf !online
        STRRegistered = False
        STRBootstrapped = False
    EndIf
    STRWasConnected = online
    If online && STRInside
        If !STRRegistered
            STRMissivesBridge.OpenBoard(MissiveBoard.GetFormID(), GetFormID())
            STRRegistered = True
        EndIf
        ; CanGenerate includes THIS board's lease and the quest reservation.
        ; No refresh date is consumed while handshake/election is pending.
        If STRCanRefresh()
            If !STRBootstrapped
                ; Bootstrap only stopped slots, preserving every running or
                ; claimed instance. Existing save cooldown must not prevent
                ; an empty first shared board from ever starting generation.
                STRUpdateBoard(True)
                STRBootstrapped = True
            Else
                STRUpdateBoard(False)
            EndIf
        EndIf
        STRRefreshList(QuestsLow)
        STRRefreshList(QuestsMed)
        STRRefreshList(QuestsHigh)
        STRRefreshList(QuestsVeryHigh)
        STRMissivesBridge.BoardChanged(MissiveBoard.GetFormID())
    EndIf
    ; Keep watching a loaded trigger even when the player connected while
    ; already inside it. Cell detach cancels the timer.
    RegisterForSingleUpdate(1.0)
EndEvent

Bool Function STRCanRefresh()
    If STRCanRefreshList(QuestsLow)
        Return True
    ElseIf STRCanRefreshList(QuestsMed)
        Return True
    ElseIf STRCanRefreshList(QuestsHigh)
        Return True
    ElseIf STRCanRefreshList(QuestsVeryHigh)
        Return True
    EndIf
    Return False
EndFunction

Bool Function STRCanRefreshList(FormList missions)
    Int i = 0
    While i < missions.GetSize()
        Quest mission = missions.GetAt(i) as Quest
        If mission && STRMissivesBridge.CanGenerate(mission.GetFormID(), MissiveBoard.GetFormID())
            Return True
        EndIf
        i += 1
    EndWhile
    Return False
EndFunction

Function STRRefreshList(FormList missions)
    Int i = 0
    While i < missions.GetSize()
        STRMissivesBridge.RefreshPosting(missions.GetAt(i) as Quest)
        i += 1
    EndWhile
EndFunction

Function STRUpdateBoard(Bool bootstrap = False)
    If !bootstrap && GameDaysPassed.GetValue() <= LastUpdate + RefreshRate.GetValue()
        Return
    EndIf
    If STRMissivesBridge.IsConnected() && !STRCanRefresh()
        Return
    EndIf
    MissiveBoard.BlockActivation(True)
    Bool low = UpdateQuests(QuestChanceLow.GetValue(), QuestsLow, bootstrap)
    Bool med = UpdateQuests(QuestChanceMed.GetValue(), QuestsMed, bootstrap)
    Bool high = UpdateQuests(QuestChanceHigh.GetValue(), QuestsHigh, bootstrap)
    Bool veryHigh = UpdateQuests(QuestChanceVeryHigh.GetValue(), QuestsVeryHigh, bootstrap)
    If low || med || high || veryHigh
        LastUpdate = GameDaysPassed.GetValue()
        Debug.Trace("STR Missives refresh attempted: bootstrap=" + bootstrap)
    EndIf
    MissiveBoard.BlockActivation(False)
EndFunction

Bool Function UpdateQuests(Float QuestChance, FormList QuestList, Bool onlyStart = False)
    Bool eligible = False
    Int QuestIndex = 0
    While QuestIndex < QuestList.GetSize()
        Quest MissiveQuest = QuestList.GetAt(QuestIndex) as Quest
        If MissiveQuest && (!STRMissivesBridge.IsConnected() || STRMissivesBridge.CanGenerate(MissiveQuest.GetFormID(), MissiveBoard.GetFormID()))
            eligible = True
            If Utility.RandomInt() < QuestChance
                If !MissiveQuest.IsRunning()
                    Bool started = MissiveQuest.Start()
                    Debug.Trace("STR Missives quest start: quest=" + MissiveQuest + ", success=" + started)
                ElseIf !onlyStart && MissiveQuest.GetStage() == 0
                    MissiveQuest.SetStage(110)
                EndIf
            EndIf
        EndIf
        QuestIndex += 1
    EndWhile
    Return eligible
EndFunction
