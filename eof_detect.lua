-- writes a flag file when playback reaches natural end of file
local flag_file = os.getenv("KRONO_EOF_FILE")
if not flag_file then return end

mp.register_event("end-file", function(event)
    if event.reason == "eof" then
        local f = io.open(flag_file, "w")
        if f then f:write("1"); f:close() end
    end
end)
