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
Float STRFallbackDelay = 0.0
Int STRFallbackCursor = 0
Quest STRFallbackQuest
Bool STRFallbackWaiting = False
Bool STRInside = False
Bool STRWasConnected = False
Bool STRRegistered = False

Event OnInit()
    RegisterForSingleUpdate(0.5)
EndEvent

Event OnLoad()
    STRRegistered = False
    RegisterForSingleUpdate(0.5)
EndEvent

Event OnCellAttach()
    RegisterForSingleUpdate(0.5)
EndEvent

Event OnCellDetach()
    If STRRegistered && STRMissivesBoardBridge.IsConnected()
        STRMissivesBoardBridge.CloseBoard(MissiveBoard.GetFormID())
    EndIf
    STRRegistered = False
    STRInside = False
    UnregisterForUpdate()
EndEvent

Event OnTriggerEnter(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        STRInside = True
        If STRMissivesBoardBridge.IsConnected()
            If !STRRegistered
                STRMissivesBoardBridge.OpenBoard(MissiveBoard.GetFormID(), GetFormID())
                STRRegistered = True
            EndIf
            RegisterForSingleUpdate(0.5)
        Else
            STRUpdateBoard(False)
        EndIf
    EndIf
EndEvent

Event OnTriggerLeave(ObjectReference akActionRef)
    If akActionRef == Game.GetPlayer()
        STRInside = False
        If STRRegistered && STRMissivesBoardBridge.IsConnected()
            STRMissivesBoardBridge.CloseBoard(MissiveBoard.GetFormID())
        EndIf
        STRRegistered = False
        UnregisterForUpdate()
    EndIf
EndEvent

Event OnUpdate()
    Bool online = STRMissivesBoardBridge.IsConnected()
    If online != STRWasConnected
        STRRegistered = False
        STRWasConnected = online
    EndIf

    If STRInside && online
        If !STRRegistered
            STRMissivesBoardBridge.OpenBoard(MissiveBoard.GetFormID(), GetFormID())
            STRRegistered = True
        EndIf
        If STRMissivesBoardBridge.IsBoardReady(MissiveBoard.GetFormID())
            STRUpdateBoard(False)
            STRRefreshList(QuestsLow)
            STRRefreshList(QuestsMed)
            STRRefreshList(QuestsHigh)
            STRRefreshList(QuestsVeryHigh)
            STRMaintainNonEmptyBoard()
        EndIf
    ElseIf STRInside
        STRRegistered = False
        STRUpdateBoard(False)
    EndIf
    If STRInside
        RegisterForSingleUpdate(1.0)
    EndIf
EndEvent

Function STRRefreshList(FormList missions)
    Int index = 0
    While index < missions.GetSize()
        Quest mission = missions.GetAt(index) as Quest
        If mission
            STRMissivesBoardBridge.RefreshPosting(mission, MissiveBoard)
        EndIf
        index += 1
    EndWhile
EndFunction

Function STRMaintainNonEmptyBoard()
    Int boardId = MissiveBoard.GetFormID()
    If !STRMissivesBoardBridge.IsBoardAuthority(boardId)
        STRFallbackWaiting = False
        STRFallbackQuest = None
        Return
    EndIf
    If STRMissivesBoardBridge.GetPostingCount(boardId) > 0
        STRFallbackWaiting = False
        STRFallbackQuest = None
        Return
    EndIf

    If STRFallbackWaiting
        STRFallbackDelay -= 1.0
        If STRFallbackDelay > 0.0
            Return
        EndIf
        If STRFallbackQuest
            Int aliasId = STRMissivesBoardBridge.GetPostingAlias(STRFallbackQuest.GetFormID())
            ObjectReference letter = None
            If aliasId >= 0
                ReferenceAlias posting = STRFallbackQuest.GetAlias(aliasId) as ReferenceAlias
                If posting
                    letter = posting.GetReference()
                EndIf
            EndIf
            STRMissivesBoardBridge.STRRemoveLocalPosting(letter, None, MissiveBoard)
            If STRFallbackQuest.IsRunning() && STRFallbackQuest.GetStage() == 0
                STRFallbackQuest.Stop()
            EndIf
        EndIf
        STRFallbackQuest = None
        STRFallbackWaiting = False
    EndIf

    Int total = QuestsLow.GetSize() + QuestsMed.GetSize() + QuestsHigh.GetSize() + QuestsVeryHigh.GetSize()
    Int attempts = 0
    While attempts < total
        If STRFallbackCursor >= total
            STRFallbackCursor = 0
        EndIf
        Quest mission = STRGetQuestAt(STRFallbackCursor)
        STRFallbackCursor += 1
        attempts += 1
        If mission && STRMissivesBoardBridge.CanGenerate(mission.GetFormID(), boardId)
            If !mission.IsRunning() && mission.Start()
                STRFallbackQuest = mission
                STRFallbackWaiting = True
                STRFallbackDelay = 6.0
                Debug.Trace("STR Missives board fallback started quest " + mission.GetFormID())
                Return
            ElseIf mission.IsRunning() && mission.GetStage() == 0
                STRMissivesBoardBridge.RefreshPosting(mission, MissiveBoard)
            EndIf
        EndIf
    EndWhile
EndFunction

Quest Function STRGetQuestAt(Int index)
    If index < QuestsLow.GetSize()
        Return QuestsLow.GetAt(index) as Quest
    EndIf
    index -= QuestsLow.GetSize()
    If index < QuestsMed.GetSize()
        Return QuestsMed.GetAt(index) as Quest
    EndIf
    index -= QuestsMed.GetSize()
    If index < QuestsHigh.GetSize()
        Return QuestsHigh.GetAt(index) as Quest
    EndIf
    index -= QuestsHigh.GetSize()
    If index < QuestsVeryHigh.GetSize()
        Return QuestsVeryHigh.GetAt(index) as Quest
    EndIf
    Return None
EndFunction

Function STRUpdateBoard(Bool bootstrap = False)
    If STRMissivesBoardBridge.IsConnected()
        Int boardId = MissiveBoard.GetFormID()
        If !STRMissivesBoardBridge.IsBoardReady(boardId) || !STRMissivesBoardBridge.IsBoardAuthority(boardId)
            Return
        EndIf
        If bootstrap || GameDaysPassed.GetValue() > LastUpdate + RefreshRate.GetValue()
            MissiveBoard.BlockActivation(True)
            UpdateQuests(QuestChanceLow.GetValue(), QuestsLow)
            UpdateQuests(QuestChanceMed.GetValue(), QuestsMed)
            UpdateQuests(QuestChanceHigh.GetValue(), QuestsHigh)
            UpdateQuests(QuestChanceVeryHigh.GetValue(), QuestsVeryHigh)
            MissiveBoard.BlockActivation(False)
            LastUpdate = GameDaysPassed.GetValue()
            Debug.Trace("STR Missives board authority generated local postings")
        EndIf
        Return
    EndIf

    If GameDaysPassed.GetValue() <= LastUpdate + RefreshRate.GetValue()
        Return
    EndIf
    LastUpdate = GameDaysPassed.GetValue()
    MissiveBoard.BlockActivation(True)
    UpdateQuests(QuestChanceLow.GetValue(), QuestsLow)
    UpdateQuests(QuestChanceMed.GetValue(), QuestsMed)
    UpdateQuests(QuestChanceHigh.GetValue(), QuestsHigh)
    UpdateQuests(QuestChanceVeryHigh.GetValue(), QuestsVeryHigh)
    MissiveBoard.BlockActivation(False)
    Debug.Trace("Missives: Quests Updated")
EndFunction

Function UpdateQuests(Float QuestChance, FormList QuestList)
    Int QuestIndex = 0
    While QuestIndex < QuestList.GetSize()
        If Utility.RandomInt() < QuestChance
            Quest MissiveQuest = QuestList.GetAt(QuestIndex) as Quest
            If MissiveQuest && (!STRMissivesBoardBridge.IsConnected() || STRMissivesBoardBridge.CanGenerate(MissiveQuest.GetFormID(), MissiveBoard.GetFormID()))
                If !MissiveQuest.IsRunning()
                    Bool Started = MissiveQuest.Start()
                    If Started
                        Debug.Trace("STR Missives starting quest " + MissiveQuest.GetFormID())
                    EndIf
                ElseIf !STRMissivesBoardBridge.IsConnected() && MissiveQuest.GetStage() == 0
                    MissiveQuest.SetStage(110)
                EndIf
            EndIf
        EndIf
        QuestIndex += 1
    EndWhile
EndFunction
