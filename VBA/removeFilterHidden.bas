Attribute VB_Name = "removeFilterHidden"
Sub RemoveHiddenRows()
    Dim xRow As Range
    Dim xRg As Range
    Dim xRows As Range
    On Error Resume Next
    Set xRows = Intersect(ActiveSheet.Range("A:A").EntireRow, ActiveSheet.UsedRange)
    If xRows Is Nothing Then Exit Sub
        For Each xRow In xRows.Columns(1).Cells
            If xRow.EntireRow.Hidden Then
                If xRg Is Nothing Then
                    Set xRg = xRow
                Else
                    Set xRg = Union(xRg, xRow)
                End If
            End If
        Next
        If Not xRg Is Nothing Then
            MsgBox xRg.Count & " hidden rows have been deleted", , "Kutools for Excel"
            xRg.EntireRow.Delete
        Else
            MsgBox "No hidden rows found", , "Kutools for Excel"
        End If
    End Sub
