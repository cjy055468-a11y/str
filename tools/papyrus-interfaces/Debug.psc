; Compile-only native interface. Never ship this as a runtime script.
Scriptname Debug Hidden
Function Trace(String asTextToPrint, Int aiSeverity=0) Global Native
Function Notification(String asNotificationText) Global Native
Function MessageBox(String asMessageBoxText) Global Native
