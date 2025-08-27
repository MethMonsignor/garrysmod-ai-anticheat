-- garrysmod/addons/ai_anticheat/lua/autorun/server/ai_anticheat.lua

util.AddNetworkString("AC_SendData")

local thresholds = {
  aimbot        = 0.85, triggerbot    = 0.80, silent_aim    = 0.80,
  no_recoil     = 0.75, speedhack     = 0.90, bunny_hop     = 0.80,
  teleport      = 0.95, wallhack      = 0.85, spinbot       = 0.90,
  lag_switch    = 0.90, lua_injection = 0.70, memory_inject = 0.70,
  net_flood     = 0.95, score_spoof   = 0.80, model_corrupt = 0.80,
  ghost_inputs  = 0.85
}
local anomalyThreshold = -0.1

local function enforcePermBan(ply, vector, prob, anomaly)
  local steamID   = ply:SteamID()
  local steamID64 = util.SteamIDTo64(steamID)
  local reason    = string.format("AI-Detected %s (%.2f, Anom: %.2f)", vector, prob, anomaly)

  ply:Ban(0, reason)
  ply:Kick(reason)
  RunConsoleCommand("writeid")

  logCheatEvent({
    nick       = ply:Nick(),
    steamID    = steamID,
    steamID64  = steamID64,
    vector     = vector,
    probability= prob,
    anomaly    = anomaly,
    reason     = reason,
    timestamp  = os.date("!%Y-%m-%dT%H:%M:%SZ")
  })
end

hook.Add("PlayerTick", "AC_DetectAndBan", function(ply, mv)
  local now       = SysTime()
  local dt        = now - (ply.AC_LastTime or now)
  ply.AC_LastTime = now

  local lastAng   = ply.AC_LastAng or mv:GetAngles()
  ply.AC_LastAng  = mv:GetAngles()

  local data = {
    speed               = mv:GetVelocity():Length() / math.max(dt,0.001),
    ang_rate            = (mv:GetAngles() - lastAng):Length() / math.max(dt,0.001),
    packet_rate         = (mv:GetCurrentCommand():CommandNumber() - (ply.LastCmd or 0)) / math.max(dt,0.001),
    reaction_time       = ply.LastShot and (CurTime() - ply.LastShot) or 0,
    los_violation       = util.TraceLine({start=mv:GetOrigin(), endpos=Vector(0,0,0), filter=ply}).HitWorld and 1 or 0,
    model_hash          = util.CRC(ply:GetModel()),
    expected_model_hash = ply.OriginalModelHash or "",
    ping                = ply:Ping(),
    loaded_modules      = engine.GetModules()
  }
  ply.LastCmd = mv:GetCurrentCommand():CommandNumber()

  HTTP({
    url     = "http://127.0.0.1:5000/predict",
    method  = "POST",
    headers = {["Content-Type"]="application/json"},
    body    = util.TableToJSON(data),
    success = function(_,body)
      local res = util.JSONToTable(body)
      for vector,prob in pairs(res.vector_probabilities) do
        if prob > (thresholds[vector] or 1) or res.anomaly_score < anomalyThreshold then
          enforcePermBan(ply, vector, prob, res.anomaly_score)
          return
        end
      end
    end,
    failure = function(_,err)
      print("[AC] Prediction API error:", err)
    end
  })
end)
