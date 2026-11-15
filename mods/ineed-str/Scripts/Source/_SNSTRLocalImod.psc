Scriptname _SNSTRLocalImod extends ActiveMagicEffect

; These property names match iNeed's original magicImodScript VMAD.
ImageSpaceModifier Property IntroFX Auto
ImageSpaceModifier Property StaticFX Auto
ImageSpaceModifier Property OutroFX Auto
Float Property fStaticDelay Auto

Bool Finishing
Bool LocalEffect

Event OnEffectStart(Actor akTarget, Actor akCaster)
    LocalEffect = akTarget == Game.GetPlayer()
    If !LocalEffect
        Return
    EndIf
    If IntroFX
        IntroFX.Apply()
    EndIf
    Utility.Wait(fStaticDelay)
    If !Finishing && StaticFX
        StaticFX.Apply()
    EndIf
EndEvent

Event OnEffectFinish(Actor akTarget, Actor akCaster)
    Finishing = True
    ; A remote player's finish must not remove this client's own drunk image.
    If !LocalEffect || akTarget != Game.GetPlayer()
        Return
    EndIf
    If OutroFX
        OutroFX.Apply()
    EndIf
    If StaticFX
        StaticFX.Remove()
    EndIf
EndEvent
