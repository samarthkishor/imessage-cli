on run {first_name, last_name}
    tell application "Contacts" to get the value of phones of (first person whose (first name is first_name and last name is last_name))
end run
