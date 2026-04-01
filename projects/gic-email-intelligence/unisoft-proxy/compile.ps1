# compile.ps1 — run from Mac, deploys to EC2 via S3+SSM
# Usage: pwsh compile.ps1 [run|compile|deploy]

$S3Bucket = "indemn-assets"
$S3Key = "unisoft/UniProxy.cs"
$InstanceId = "i-0dc2563c9bc92aa0e"
$LocalFile = "$PSScriptRoot/UniProxy.cs"
$RemoteDir = "C:\unisoft"
$CscPath = "C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
$References = "System.ServiceModel.dll", "System.Runtime.Serialization.dll", "System.ServiceProcess.dll", "System.Web.Extensions.dll", "System.Xml.dll"

# Upload
aws s3 cp $LocalFile "s3://$S3Bucket/$S3Key"

# Build JSON params for SSM
$refArgs = ($References | ForEach-Object { "/reference:$_" }) -join " "
$presigned = aws s3 presign "s3://$S3Bucket/$S3Key" --expires-in 300

# Commands: download, compile, optionally run
$cmds = @(
    "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12"
    "Invoke-WebRequest -Uri '$presigned' -OutFile '$RemoteDir\UniProxy.cs'"
    "& '$CscPath' /out:$RemoteDir\UniProxy.exe $refArgs $RemoteDir\UniProxy.cs 2>&1"
    "if (Test-Path '$RemoteDir\UniProxy.exe') { Write-Output 'COMPILED OK' } else { Write-Output 'COMPILE FAILED' }"
)

# Add run command if requested
if ($args[0] -eq "run") {
    $cmds += "& '$RemoteDir\UniProxy.exe' 2>&1"
}

$params = @{ commands = $cmds } | ConvertTo-Json
$params | Out-File /tmp/ssm-params.json

$cmdId = aws ssm send-command `
    --instance-ids $InstanceId `
    --document-name "AWS-RunPowerShellScript" `
    --parameters file:///tmp/ssm-params.json `
    --timeout-seconds 120 `
    --output text --query 'Command.CommandId'

Write-Host "SSM Command: $cmdId"
Write-Host "Waiting..."
Start-Sleep -Seconds 15

$result = aws ssm get-command-invocation `
    --command-id $cmdId `
    --instance-id $InstanceId `
    --output json | ConvertFrom-Json

Write-Host "Status: $($result.Status)"
Write-Host $result.StandardOutputContent
if ($result.StandardErrorContent) { Write-Host "STDERR: $($result.StandardErrorContent)" }
