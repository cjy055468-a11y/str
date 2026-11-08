;BEGIN FRAGMENT CODE - Do not edit anything between this and the end comment
;NEXT FRAGMENT INDEX 10
Scriptname _M_QuestTrackFugitiveScript Extends Quest Hidden

;BEGIN ALIAS PROPERTY Inn2
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Inn2 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Missive
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Missive Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY OtherHold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_OtherHold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Hold
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Hold Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY InnMarker2
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_InnMarker2 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Steward
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Steward Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Inn1
;ALIAS PROPERTY TYPE LocationAlias
LocationAlias Property Alias_Inn1 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Criminal
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Criminal Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY Jarl
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_Jarl Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY InnMarker1
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_InnMarker1 Auto
;END ALIAS PROPERTY

;BEGIN ALIAS PROPERTY MissiveBoard
;ALIAS PROPERTY TYPE ReferenceAlias
ReferenceAlias Property Alias_MissiveBoard Auto
;END ALIAS PROPERTY

;BEGIN FRAGMENT Fragment_0
Function Fragment_0()
;BEGIN CODE
SetObjectiveDisplayed(20)

if(Alias_Criminal.GetActorRef().IsDead())
SetStage(40)
endIf
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_4
Function Fragment_4()
;BEGIN CODE
CompleteAllObjectives()
Game.GetPlayer().AddItem(Gold001, GoldReward.GetValue() as int)
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_8
Function Fragment_8()
;BEGIN CODE
if(Alias_MissiveBoard.GetRef().GetItemCount(Alias_Missive.GetRef()) > 0)
Alias_MissiveBoard.GetRef().RemoveItem(Alias_Missive.GetRef())
;Debug.Trace("Missive Removed from Board")
elseif(Game.GetPlayer().GetItemCount(Alias_Missive.GetRef()) > 0)
Game.GetPlayer().RemoveItem(Alias_Missive.GetRef())
;Debug.Trace("Missive Removed from Player")
endIf

while(Alias_Criminal.GetRef().Is3DLoaded())
Utility.Wait(1.0)
endWhile
Alias_Criminal.GetRef().Disable()

Stop()
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_6
Function Fragment_6()
;BEGIN CODE
FailAllObjectives()
SetStage(110)
;END CODE
EndFunction
;END FRAGMENT

;BEGIN FRAGMENT Fragment_2
Function Fragment_2()
;BEGIN CODE
SetObjectiveCompleted(20)
if(Alias_Steward.GetRef())
SetObjectiveDisplayed(40)
else
SetObjectiveDisplayed(41)
endIf
;END CODE
EndFunction
;END FRAGMENT

;END FRAGMENT CODE - Do not edit anything between this and the begin comment

MiscObject Property Gold001  Auto

GlobalVariable Property GoldReward  Auto
