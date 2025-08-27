-- garrysmod/addons/ai_anticheat/lua/autorun/server/ac_ban_check.lua

hook.Add("CheckPassword", "AC_PermBanCheck", function(steamID64, ip, svPass, clPass)
  local banlist = file.Read("cfg/banlist.cfg", "GAME") or ""
  if banlist:find(steamID64, 1, true) then
    return false, "You are permanently banned from this server."
  end
end)
