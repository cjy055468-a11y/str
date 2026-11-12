Scriptname STRNoticeBridge Hidden Native

Bool Function IsConnected() Global Native
Bool Function IsReady() Global Native
Bool Function IsBoardReady(Int boardId) Global Native
Bool Function IsBoardAuthority(Int boardId) Global Native
Int Function GetNoticeState(Int questId, Int boardId) Global Native
Int Function GetProxyBook(Int questId) Global Native
Int Function GetOriginalBook(Int questId) Global Native
Bool Function IsLocalTask(Int questId) Global Native
Bool Function IsClaimPending(Int questId) Global Native
Bool Function IsOriginalBookProtected(Int questId) Global Native
Int Function GetPostingCount(Int boardId) Global Native
Function OpenBoard(Int boardId) Global Native
Function CloseBoard(Int boardId) Global Native
Function Offer(Int questId, Int boardId) Global Native
Bool Function BeginClaim(Int questId, Int boardId) Global Native
Function CommitClaim(Int questId, Int boardId) Global Native
Function ReleaseClaim(Int questId, Int boardId) Global Native
Function EndClaim(Int questId, Int boardId) Global Native
Function MarkLocalTask(Int questId) Global Native
