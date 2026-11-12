Scriptname STRNoticeSlip extends ObjectReference

Quest Property Mission Auto
Int Property PostingAlias Auto
Int Property BoardAlias Auto
Container Property BoardBase Auto

ObjectReference NoticeBoard
ObjectReference CurrentContainer
ObjectReference PreparedLetter
ObjectReference PreparedSource
Bool NoticeActive = False
Bool NoticeDone = False
Bool NoticeLoopRunning = False
Bool StartedHere = False
Bool Prepared = False
Bool CommitSent = False
Bool LetterDelivered = False
Int WaitTicks = 0
Int PrepareTicks = 0

Event OnContainerChanged(ObjectReference akNewContainer, ObjectReference akOldContainer)
    CurrentContainer = akNewContainer
    If NoticeDone
        Return
    EndIf
    If NoticeActive
        If akNewContainer != Game.GetPlayer() && !CommitSent
            AbortClaim(False)
        EndIf
        Return
    EndIf
    If akNewContainer != Game.GetPlayer()
        Return
    EndIf
    ; Only taking a public slip from an actual Missives board can claim it.
    If !akOldContainer || !BoardBase || akOldContainer.GetBaseObject() != BoardBase
        DestroySlip()
        Return
    EndIf
    NoticeBoard = akOldContainer
    If !Mission || !STRNoticeBridge.IsConnected()
        DestroySlip()
        Return
    EndIf
    If STRNoticeBridge.IsLocalTask(Mission.GetFormID()) || (Mission.IsRunning() && Mission.GetStage() >= 20)
        Debug.Notification("你已经承接了这一类委托，请先完成手中的任务。")
        DestroySlip()
        Return
    EndIf
    If !STRNoticeBridge.BeginClaim(Mission.GetFormID(), NoticeBoard.GetFormID())
        DestroySlip()
        Return
    EndIf
    NoticeActive = True
    ClaimLoop()
EndEvent

Event OnUpdate()
    ClaimLoop()
EndEvent

Function ClaimLoop()
    If NoticeLoopRunning
        Return
    EndIf
    NoticeLoopRunning = True
    While NoticeActive && !NoticeDone && Mission && NoticeBoard
        ProcessClaim()
        If NoticeActive && !NoticeDone
            Utility.WaitMenuMode(1.0)
        EndIf
    EndWhile
    NoticeLoopRunning = False
EndFunction

Function ProcessClaim()
    If !NoticeActive || NoticeDone || !Mission || !NoticeBoard
        Return
    EndIf
    ; An unacknowledged commit may already have won on the server. Keep its
    ; receipt alive across a temporary disconnect rather than dropping the task.
    If !STRNoticeBridge.IsConnected() || !STRNoticeBridge.IsReady()
        Return
    EndIf
    Int questId = Mission.GetFormID()
    Int boardId = NoticeBoard.GetFormID()
    Int noticeStatus = STRNoticeBridge.GetNoticeState(questId, boardId)
    If noticeStatus == 2
        If !Prepared
            If !PrepareTask()
                If PrepareTicks >= 6
                    AbortClaim(True)
                EndIf
                Return
            EndIf
        EndIf
        If !NoticeActive || NoticeDone || CurrentContainer != Game.GetPlayer()
            Return
        EndIf
        CommitSent = True
        STRNoticeBridge.CommitClaim(questId, boardId)
    ElseIf noticeStatus == 4
        DeliverTask()
        Return
    ElseIf noticeStatus == 1 || noticeStatus == 3 || noticeStatus == 5 || noticeStatus < 0
        AbortClaim(False)
        Return
    ElseIf noticeStatus == 0
        ; A reservation can be released while this local preparation is pending.
        AbortClaim(False)
        Return
    ElseIf noticeStatus == 6
        WaitTicks += 1
        If WaitTicks >= 60
            AbortClaim(True)
            Return
        EndIf
    EndIf
EndFunction

Bool Function PrepareTask()
    PrepareTicks += 1
    If Mission.IsRunning() && Mission.GetStage() >= 20
        PrepareTicks = 6
        Return False
    EndIf
    ; Discard an old unaccepted solo instance. Public rendering may have
    ; removed its old letter; the claimant needs newly filled local aliases.
    If PrepareTicks == 1 && Mission.IsRunning() && Mission.GetStage() < 20
        ReferenceAlias previousPosting = Mission.GetAlias(PostingAlias) as ReferenceAlias
        ReferenceAlias previousBoard = Mission.GetAlias(BoardAlias) as ReferenceAlias
        ObjectReference previousLetter = None
        ObjectReference previousSource = None
        If previousPosting
            previousLetter = previousPosting.GetReference()
        EndIf
        If previousBoard
            previousSource = previousBoard.GetReference()
        EndIf
        If previousLetter && previousSource && previousSource.GetItemCount(previousLetter) > 0
            previousSource.RemoveItem(previousLetter, 1, True)
        EndIf
        Mission.Stop()
    EndIf
    If !Mission.IsRunning()
        If !Mission.Start()
            PrepareTicks = 6
            Return False
        EndIf
        StartedHere = True
    EndIf
    ReferenceAlias posting = Mission.GetAlias(PostingAlias) as ReferenceAlias
    ReferenceAlias source = Mission.GetAlias(BoardAlias) as ReferenceAlias
    If posting
        PreparedLetter = posting.GetReference()
    EndIf
    If source
        PreparedSource = source.GetReference()
    EndIf
    If !PreparedLetter || !PreparedSource
        Return False
    EndIf
    Prepared = True
    Return True
EndFunction

Function DeliverTask()
    ; Re-validate the actual local task before running any acceptance fragment.
    ; A successful receipt remains pending if delivery temporarily cannot finish.
    If !Prepared
        If !PrepareTask()
            Debug.Trace("STR public notice: committed receipt waiting for local task " + Mission.GetFormID())
            Return
        EndIf
    EndIf
    STRNoticeBridge.MarkLocalTask(Mission.GetFormID())
    If !LetterDelivered
        If !PreparedLetter
            Return
        EndIf
        If Game.GetPlayer().GetItemCount(PreparedLetter) <= 0
            If PreparedSource && PreparedSource.GetItemCount(PreparedLetter) > 0
                PreparedSource.RemoveItem(PreparedLetter, 1, True, Game.GetPlayer())
            Else
                Game.GetPlayer().AddItem(PreparedLetter, 1, True)
            EndIf
        EndIf
        LetterDelivered = Game.GetPlayer().GetItemCount(PreparedLetter) > 0
        If !LetterDelivered
            Return
        EndIf
    EndIf
    Bool accepted = Mission.GetStage() >= 20
    If !accepted
        accepted = Mission.SetStage(20)
    EndIf
    If !accepted
        Return
    EndIf
    STRNoticeBridge.EndClaim(Mission.GetFormID(), NoticeBoard.GetFormID())
    NoticeActive = False
    DestroySlip()
EndFunction

Function AbortClaim(Bool explainFailure)
    If NoticeDone
        Return
    EndIf
    If Mission && NoticeBoard
        STRNoticeBridge.ReleaseClaim(Mission.GetFormID(), NoticeBoard.GetFormID())
    EndIf
    If StartedHere && Mission && Mission.IsRunning() && Mission.GetStage() < 20
        ; Capture/remove created objects before Stop clears the aliases.
        If PreparedLetter
            If PreparedSource && PreparedSource.GetItemCount(PreparedLetter) > 0
                PreparedSource.RemoveItem(PreparedLetter, 1, True)
            EndIf
            If Game.GetPlayer().GetItemCount(PreparedLetter) > 0
                Game.GetPlayer().RemoveItem(PreparedLetter, 1, True)
            EndIf
        EndIf
        Mission.Stop()
    EndIf
    If Mission && NoticeBoard
        STRNoticeBridge.EndClaim(Mission.GetFormID(), NoticeBoard.GetFormID())
    EndIf
    If explainFailure
        Debug.Notification("暂时无法承接此委托，请尝试其他告示。")
    EndIf
    NoticeActive = False
    DestroySlip()
EndFunction

Function DestroySlip()
    NoticeDone = True
    NoticeActive = False
    UnregisterForUpdate()
    If CurrentContainer && CurrentContainer.GetItemCount(Self) > 0
        CurrentContainer.RemoveItem(Self, 1, True)
    Else
        DisableNoWait()
    EndIf
    Delete()
EndFunction
