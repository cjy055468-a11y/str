Scriptname _SNSTRConsumeRelay extends Quest

Spell Property ResetPulse Auto
Spell Property EatPulse Auto
Spell Property DrinkPulse Auto
Spell Property ChairEatPulse Auto
Spell Property ChairDrinkPulse Auto
Spell Property StopPulse Auto
Idle Property IdleStop_Loose Auto

Actor[] RemoteActors
Int[] RemoteTokens
Int[] RemoteEpochs
Int[] PreviousEpochs
Int[] RemoteActions
Float[] RemoteDeadlines
Bool[] RemoteStarted
Int Sequence
Int Epoch
Int RemoteCount
Int LocalToken
Int LocalAction
Float LocalDeadline
Bool ResetPending = True

_SNSTRConsumeRelay Function GetRelay() Global
    _SNSTRConsumeRelay relay = Game.GetFormFromFile(0x800, "iNeed_STR_Compatibility.esp") as _SNSTRConsumeRelay
    If relay && !relay.IsRunning()
        relay.Start()
    EndIf
    Return relay
EndFunction

Function EnsureArrays()
    If !RemoteActors
        RemoteActors = New Actor[128]
        RemoteTokens = New Int[128]
        RemoteEpochs = New Int[128]
        PreviousEpochs = New Int[128]
        RemoteActions = New Int[128]
        RemoteDeadlines = New Float[128]
        RemoteStarted = New Bool[128]
    EndIf
EndFunction

Function ResetForLoad()
    UnregisterForUpdate()
    UnregisterForAllControls()
    LocalToken = 0
    LocalAction = 0
    ResetPending = True
    ; Real-time deadlines cannot survive a process restart or save rollback.
    RemoteActors = New Actor[128]
    RemoteTokens = New Int[128]
    RemoteEpochs = New Int[128]
    PreviousEpochs = New Int[128]
    RemoteActions = New Int[128]
    RemoteDeadlines = New Float[128]
    RemoteStarted = New Bool[128]
    RemoteCount = 0
EndFunction

Spell Function Marker(Int action)
    If action == 0
        Return ResetPulse
    ElseIf action == 1
        Return EatPulse
    ElseIf action == 2
        Return DrinkPulse
    ElseIf action == 3
        Return ChairEatPulse
    ElseIf action == 4
        Return ChairDrinkPulse
    EndIf
    Return StopPulse
EndFunction

Function SendPulse(Int action, Int token)
    Actor source = Game.GetPlayer()
    Spell pulse = Marker(action)
    If pulse
        source.DispelSpell(pulse)
        pulse.SetNthEffectMagnitude(0, token as Float)
        pulse.Cast(source, source)
        Debug.Trace("[iNeed-STR] consume send action=" + action + " token=" + token)
    EndIf
EndFunction

Float Function Duration(Int action)
    If action == 2 || action == 4
        Return 7.5
    EndIf
    Return 7.0
EndFunction

Function PlayAction(Actor target, Int action)
    If action == 1
        Debug.SendAnimationEvent(target, "idleEatingStandingStart")
    ElseIf action == 2
        Debug.SendAnimationEvent(target, "idleDrinkingStandingStart")
    ElseIf action == 3
        Debug.SendAnimationEvent(target, "ChairEatingStart")
    ElseIf action == 4
        Debug.SendAnimationEvent(target, "ChairDrinkingStart")
    EndIf
EndFunction

Int Function BeginLocal(Actor source, Int action)
    If source != Game.GetPlayer() || action < 1 || action > 4
        Return 0
    EndIf
    If LocalToken > 0
        EndLocal(LocalToken, False)
    EndIf
    If ResetPending || Sequence >= 255
        Int oldEpoch = Epoch
        Epoch = Utility.RandomInt(1, 65535)
        If Epoch == oldEpoch
            Epoch = (Epoch % 65535) + 1
        EndIf
        Sequence = 0
        ResetPending = False
        SendPulse(0, Epoch * 256)
    EndIf
    Sequence += 1
    ; A 16-bit session and 8-bit sequence fit exactly in an IEEE float magnitude.
    LocalToken = Epoch * 256 + Sequence
    LocalAction = action
    LocalDeadline = Utility.GetCurrentRealTime() + Duration(action) + 0.75
    SendPulse(action, LocalToken)
    RegisterForControl("Forward")
    RegisterForControl("Back")
    RegisterForControl("Strafe Left")
    RegisterForControl("Strafe Right")
    RegisterForControl("Jump")
    RegisterForControl("Sneak")
    RegisterForControl("Ready Weapon")
    RegisterForSingleUpdate(0.25)
    Return LocalToken
EndFunction

Function EndLocal(Int token, Bool stopIdle = True)
    If token <= 0 || token != LocalToken
        Return
    EndIf
    Int action = LocalAction
    LocalToken = 0
    LocalAction = 0
    UnregisterForAllControls()
    SendPulse(5, token)
    Actor source = Game.GetPlayer()
    If stopIdle && action <= 2 && !source.IsDead() && !source.IsInCombat()
        source.PlayIdle(IdleStop_Loose)
    EndIf
EndFunction

Function InterruptLocal()
    EndLocal(LocalToken, False)
EndFunction

Event OnControlDown(String control)
    InterruptLocal()
EndEvent

Int Function FindSlot(Actor target)
    EnsureArrays()
    Int i = 0
    Int free = -1
    While i < RemoteCount
        If RemoteActors[i] == target
            Return i
        ElseIf !RemoteActors[i] || !RemoteActors[i].Is3DLoaded()
            If free < 0
                free = i
            EndIf
        EndIf
        i += 1
    EndWhile
    If free < 0 && RemoteCount < RemoteActors.Length
        free = RemoteCount
        RemoteCount += 1
    EndIf
    If free >= 0
        RemoteActors[free] = target
        RemoteTokens[free] = 0
        RemoteEpochs[free] = 0
        PreviousEpochs[free] = 0
        RemoteActions[free] = 0
        RemoteStarted[free] = False
    EndIf
    Return free
EndFunction

Function ClearRemote(Int slot, Bool stopIdle)
    Actor target = RemoteActors[slot]
    Int action = RemoteActions[slot]
    Bool wasStarted = RemoteStarted[slot]
    RemoteActions[slot] = 0
    RemoteStarted[slot] = False
    ; Seated consume events complete in their furniture graph. Never eject a
    ; remote actor from furniture with a standing idle-stop animation.
    If stopIdle && wasStarted && action >= 1 && action <= 2 && target && target.Is3DLoaded()
        If !target.IsDead() && !target.IsInCombat() && target.GetSitState() == 0
            target.PlayIdle(IdleStop_Loose)
        EndIf
    EndIf
EndFunction

Function Receive(Actor target, Int action, Int token)
    If !target || target == Game.GetPlayer() || !SkyrimTogetherUtils.IsRemotePlayer(target)
        Return
    EndIf
    If action < 0 || action > 5 || token < 256 || token > 16777215
        Return
    EndIf
    Int slot = FindSlot(target)
    If slot < 0
        Debug.Trace("[iNeed-STR] consume remote actor table full", 1)
        Return
    EndIf
    Debug.Trace("[iNeed-STR] consume receive actor=" + target + " action=" + action + " token=" + token)
    Int incomingEpoch = token / 256
    If incomingEpoch != RemoteEpochs[slot]
        ; Discard messages from the session just replaced. A start can establish
        ; its new session even when Papyrus schedules its reset marker later.
        If incomingEpoch == PreviousEpochs[slot]
            Return
        EndIf
        ClearRemote(slot, True)
        PreviousEpochs[slot] = RemoteEpochs[slot]
        RemoteEpochs[slot] = incomingEpoch
        RemoteTokens[slot] = incomingEpoch * 256
    EndIf
    If action == 0
        ; An already established session must survive a delayed reset marker.
        Return
    ElseIf action == 5
        If token >= RemoteTokens[slot]
            ClearRemote(slot, True)
            RemoteTokens[slot] = token
        EndIf
        Return
    ElseIf token <= RemoteTokens[slot]
        Return
    EndIf
    ClearRemote(slot, True)
    RemoteTokens[slot] = token
    RemoteActions[slot] = action
    RemoteDeadlines[slot] = Utility.GetCurrentRealTime() + Duration(action) + 1.5
    TryRemote(slot)
    RegisterForSingleUpdate(0.25)
EndFunction

Function TryRemote(Int slot)
    Actor target = RemoteActors[slot]
    Int action = RemoteActions[slot]
    If !RemoteStarted[slot] && target && target.Is3DLoaded() && !target.IsDead() && !target.IsInCombat()
        Int sit = target.GetSitState()
        If (action <= 2 && sit == 0) || (action >= 3 && sit == 3)
            RemoteStarted[slot] = True
            PlayAction(target, action)
        EndIf
    EndIf
EndFunction

Event OnUpdate()
    Float now = Utility.GetCurrentRealTime()
    If LocalToken > 0
        If now >= LocalDeadline || Game.GetPlayer().IsDead() || Game.GetPlayer().IsInCombat()
            EndLocal(LocalToken)
        EndIf
    EndIf
    EnsureArrays()
    Bool pending = LocalToken > 0
    Int i = 0
    While i < RemoteCount
        If RemoteActions[i] > 0
            Actor target = RemoteActors[i]
            If !target || now >= RemoteDeadlines[i]
                ClearRemote(i, True)
            ElseIf target.IsDead() || target.IsInCombat()
                ClearRemote(i, False)
            ElseIf RemoteStarted[i] && !target.Is3DLoaded()
                ClearRemote(i, False)
            Else
                TryRemote(i)
                pending = True
            EndIf
        EndIf
        i += 1
    EndWhile
    If pending
        RegisterForSingleUpdate(0.25)
    EndIf
EndEvent
