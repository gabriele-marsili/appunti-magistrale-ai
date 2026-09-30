on run argv
  set src to POSIX file (item 1 of argv)
  set dst to POSIX file (item 2 of argv)
  tell application "Keynote"
    activate
    set d to open src
    delay 1
    export d to dst as PDF
    close d saving no
  end tell
end run
