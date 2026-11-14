Scriptname AZW_RemoveControl extends ReferenceAlias

Spell Property ControlPower Auto
Int CleanupAttempts = 0

Event OnInit()
    QueueCleanup()
EndEvent

Event OnPlayerLoadGame()
    QueueCleanup()
EndEvent

Function QueueCleanup()
    UnregisterForUpdate()
    CleanupAttempts = 0
    RegisterForSingleUpdate(1.0)
EndFunction

Event OnUpdate()
    Actor player = GetActorReference()
    If player && ControlPower && player.HasSpell(ControlPower)
        Bool removed = player.RemoveSpell(ControlPower)
        Debug.Trace("AzuriteNoControl: removed control power = " + removed)
    EndIf
    CleanupAttempts += 1
    If CleanupAttempts < 5
        RegisterForSingleUpdate(2.0)
    EndIf
EndEvent
