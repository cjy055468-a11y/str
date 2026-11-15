Scriptname _SNSTRLocalStumble extends ActiveMagicEffect

Actor Drinker
Bool Finished

Event OnEffectStart(Actor akTarget, Actor akCaster)
    If akTarget != Game.GetPlayer()
        Return
    EndIf
    Drinker = akTarget
    RegisterForSingleUpdate(Utility.RandomInt(1, 60))
EndEvent

Event OnUpdate()
    If Finished || !Drinker || Drinker != Game.GetPlayer()
        Return
    EndIf
    ; Keep iNeed's impulse and cadence; only the owning client applies physics.
    Drinker.PushActorAway(Drinker, 0)
    Drinker.ApplyHavokImpulse(Drinker.GetAngleX(), Drinker.GetAngleY(), -0.3, 125)
    If !Finished
        RegisterForSingleUpdate(Utility.RandomInt(1, 60))
    EndIf
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
    Finished = True
    UnregisterForUpdate()
EndEvent
