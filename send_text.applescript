-- script from https://stackoverflow.com/a/19483011

on run {target_phone_number, target_message}
    tell application "Messages"
        set target_service to 1st service whose service type = iMessage
        set target to buddy target_phone_number of target_service
        send target_message to target
    end tell
end run
