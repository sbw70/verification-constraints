param(
    [Parameter(Mandatory=$true)][string]$Target,
    [Parameter(Mandatory=$true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$Address = [System.Net.IPAddress]::Parse($Target)
$Stream = [System.IO.File]::Open($OutputPath, [System.IO.FileMode]::CreateNew,
    [System.IO.FileAccess]::Write, [System.IO.FileShare]::Read)
$Writer = [System.IO.StreamWriter]::new($Stream, [System.Text.UTF8Encoding]::new($false))
$Ping = [System.Net.NetworkInformation.Ping]::new()
$Sequence = 0
try {
    while ($true) {
        $Sequence++
        $Record = [ordered]@{sequence=$Sequence; utc=[DateTime]::UtcNow.ToString('o');
            target=$Address.ToString(); status=$null; roundtrip_ms=$null; error=$null}
        try {
            $Reply = $Ping.Send($Address, 1000)
            $Record.status = $Reply.Status.ToString()
            if ($Reply.Status -eq [System.Net.NetworkInformation.IPStatus]::Success) {
                $Record.roundtrip_ms = $Reply.RoundtripTime
            }
        } catch {
            $Record.status = 'ProbeError'
            $Record.error = $_.Exception.Message
        }
        $Writer.WriteLine(($Record | ConvertTo-Json -Compress))
        $Writer.Flush()
        $Stream.Flush($true)
        Start-Sleep -Milliseconds 1000
    }
} finally {
    $Ping.Dispose()
    $Writer.Dispose()
}
