Scriptname _SNSTRConsumePulse extends ActiveMagicEffect

; Invisible fire-and-forget markers use STR's existing AddTarget relay.
Int Property Action Auto

Event OnEffectStart(Actor akTarget, Actor akCaster)
    Int token = Math.Floor(GetMagnitude())
    ; End the marker immediately so rapid repeated chair consumes can recast it.
    ; Animation lifetime belongs to the relay, never OnEffectFinish.
    Dispel()
    If !akTarget || akTarget == Game.GetPlayer()
        Return
    EndIf
    If !SkyrimTogetherUtils.IsRemotePlayer(akTarget)
        Return
    EndIf
    If akCaster && akCaster != akTarget
        Return
    EndIf
    _SNSTRConsumeRelay relay = _SNSTRConsumeRelay.GetRelay()
    If relay
        relay.Receive(akTarget, Action, token)
    EndIf
EndEvent
