local ffi = require("ffi")

ffi.cdef[[
typedef void* HANDLE;
typedef unsigned long DWORD;
typedef int BOOL;
typedef void* HMODULE;

BOOL EnumProcessModules(HANDLE hProcess, HMODULE* lphModule, DWORD cb, DWORD* lpcbNeeded);
DWORD GetModuleFileNameA(HMODULE hModule, char* lpFilename, DWORD nSize);
HANDLE GetCurrentProcess(void);
]]

local psapi = ffi.load("psapi")
local kernel32 = ffi.load("kernel32")

local function GetModules()
    local process = kernel32.GetCurrentProcess()
    local modules = ffi.new("HMODULE[1024]")
    local needed = ffi.new("DWORD[1]")

    if psapi.EnumProcessModules(process, modules, ffi.sizeof(modules), needed) == 0 then
        return nil, "Module enumeration failed"
    end

    local count = needed[0] / ffi.sizeof("HMODULE")
    local results = {}

    for i = 0, count - 1 do
        local path = ffi.new("char[260]")
        if psapi.GetModuleFileNameA(modules[i], path, 260) > 0 then
            table.insert(results, ffi.string(path))
        end
    end

    return results
end

return {
    GetModules = GetModules
}
