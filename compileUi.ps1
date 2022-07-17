
Set-Location .\ui

if (!(Test-Path .\uic))
{
New-Item -itemType Directory -Name uic
}

$uic_list = Get-ChildItem -Path .\*.ui -Name

Write-Output "Compiling UI."

foreach ($uic in $uic_list) {
    $out = ".\uic\ui_" + $uic.Substring(0, $uic.Length - 3) + ".py"
    pyside6-uic -o $out $uic
    Write-Output "$uic `t->`t  $out"
}

Write-Output "Finished!"

Set-Location .\..