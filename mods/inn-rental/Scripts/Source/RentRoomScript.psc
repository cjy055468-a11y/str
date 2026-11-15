Scriptname RentRoomScript extends Actor Conditional
{Vanilla room rental with STR shared-bed permission reconciliation.}

; Keep the original script name and both original VMAD properties.
ObjectReference Property Bed Auto
WIFunctionsScript Property WI Auto

; Only the client that actually ran RentRoom owns the vanilla expiry timer.
Bool STRLocalRenter
Bool STRSharedBed

Function RentRoom(DialogueGenericScript pQuestScript)
    Bed.SetActorOwner(Game.GetPlayer().GetActorBase())
    RegisterForSingleUpdateGameTime(pQuestScript.RentHours)
    Game.GetPlayer().RemoveItem(pQuestScript.Gold, pQuestScript.RoomRentalCost.GetValueInt())
    SetActorValue("Variable09", 1.0)
    STRLocalRenter = True
    STRSharedBed = True
    ; Remote clients receive Variable09 through STR's existing actor-value sync.
    RegisterForSingleUpdate(1.0)
    WI.ShowPlayerRoom(Self, Bed)
EndFunction

Function ClearRoom()
    Bed.SetActorOwner(GetActorBase())
    UnregisterForUpdateGameTime()
    SetActorValue("Variable09", 0.0)
    STRLocalRenter = False
    STRSharedBed = False
EndFunction

Function STRRestoreSharedBed()
    If STRSharedBed && Bed
        ; Restore only a grant made by this script that is still on the bed.
        If Bed.GetActorOwner() == Game.GetPlayer().GetActorBase()
            Bed.SetActorOwner(GetActorBase())
        EndIf
    EndIf
    STRSharedBed = False
EndFunction

Function STRSyncSharedBed()
    If !Bed
        Return
    EndIf
    If GetActorValue("Variable09") == 1.0 && !IsDead()
        If Bed.GetActorOwner() != Game.GetPlayer().GetActorBase()
            Bed.SetActorOwner(Game.GetPlayer().GetActorBase())
        EndIf
        STRSharedBed = True
    Else
        STRRestoreSharedBed()
        STRLocalRenter = False
    EndIf
EndFunction

Event OnInit()
    RegisterForSingleUpdate(0.25)
EndEvent

Event OnLoad()
    STRSyncSharedBed()
    RegisterForSingleUpdate(1.0)
EndEvent

Event OnUnload()
    UnregisterForUpdate()
    ; A visitor does not leave a personal ownership grant in an unloaded inn.
    ; The actual renter keeps vanilla ownership until ClearRoom runs.
    If !STRLocalRenter
        STRRestoreSharedBed()
    EndIf
EndEvent

Event OnUpdate()
    If !Is3DLoaded() || IsDead()
        Return
    EndIf
    STRSyncSharedBed()
    RegisterForSingleUpdate(1.0)
EndEvent

Event OnUpdateGameTime()
    ClearRoom()
EndEvent

Event OnDeath(Actor akKiller)
    UnregisterForUpdate()
    ClearRoom()
EndEvent
