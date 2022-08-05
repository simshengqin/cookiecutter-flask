import subprocess

def setup_file_logging():
    subprocess.call("powershell.exe start-process -filepath '.\pylogging\procmon\Procmon.exe' -argumentlist '/accepteula /quiet /minimized /LoadConfig .\pylogging\procmon\procmon_config.pmc /backingfile ./pylogging/logs/file_logs.pml' -Passthru", shell=False)

def close_file_logging():
    print("Converting file logs to csv, please wait and do not exit the application...")
    subprocess.call("powershell.exe start-process -filepath '.\pylogging\procmon\Procmon.exe' -argumentlist '/terminate' -wait", shell=False)
    subprocess.call("powershell.exe .\pylogging\procmon\Procmon.exe /OpenLog ./pylogging/logs/file_logs.pml /SaveAs ./pylogging/logs/file_logs.csv", shell=False)
    print("Successfully saved file logs as csv")