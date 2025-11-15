-- Services
local Players = game:GetService("Players")
local LocalPlayer = Players.LocalPlayer
local Camera = game.Workspace.CurrentCamera
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local GuiService = game:GetService("GuiService")

-- Settings
local AimLock = false -- Default: Off
local FOV = 100 -- Field of view radius
local TargetPart = "HumanoidRootPart" -- Middle of body
local Smoothness = 0.1 -- Aim smoothing factor (0 to 1, lower is smoother)

-- Anti-Cheat Bypass Variables
local SpoofedProperties = {} -- Store spoofed values to mimic legitimate behavior
local RandomDelayMin = 0.01
local RandomDelayMax = 0.05 -- Randomize frame update delays for Byfron
local FakeInputDelay = math.random(0.02, 0.08) -- Simulate human input delay
local SpoofedMouseOffset = Vector3.new(0, 0, 0) -- Dynamic offset for camera spoofing

-- GUI Setup
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "AimLockGUI"
ScreenGui.Parent = game.CoreGui -- Place in CoreGui to avoid easy detection
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling

-- Main GUI Frame
local MainFrame = Instance.new("Frame")
MainFrame.Size = UDim2.new(0, 300, 0, 200)
MainFrame.Position = UDim2.new(0.5, -150, 0.5, -100)
MainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
MainFrame.BorderSizePixel = 2
MainFrame.BorderColor3 = Color3.fromRGB(0, 255, 170)
MainFrame.Active = true
MainFrame.Draggable = true
MainFrame.Parent = ScreenGui

-- Title Bar
local TitleBar = Instance.new("TextLabel")
TitleBar.Size = UDim2.new(1, 0, 0, 30)
TitleBar.Position = UDim2.new(0, 0, 0, 0)
TitleBar.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
TitleBar.Text = "AimLock v2.0"
TitleBar.TextColor3 = Color3.fromRGB(0, 255, 170)
TitleBar.Font = Enum.Font.SourceSansBold
TitleBar.TextSize = 18
TitleBar.Parent = MainFrame

-- Minimize Button
local MinimizeButton = Instance.new("TextButton")
MinimizeButton.Size = UDim2.new(0, 30, 0, 30)
MinimizeButton.Position = UDim2.new(1, -30, 0, 0)
MinimizeButton.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
MinimizeButton.Text = "-"
MinimizeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
MinimizeButton.Font = Enum.Font.SourceSansBold
MinimizeButton.TextSize = 18
MinimizeButton.Parent = MainFrame

-- Toggle Button
local ToggleButton = Instance.new("TextButton")
ToggleButton.Size = UDim2.new(0, 200, 0, 50)
ToggleButton.Position = UDim2.new(0.5, -100, 0.5, -25)
ToggleButton.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
ToggleButton.Text = "AimLock: OFF"
ToggleButton.TextColor3 = Color3.fromRGB(255, 0, 0)
ToggleButton.Font = Enum.Font.SourceSansBold
ToggleButton.TextSize = 20
ToggleButton.Parent = MainFrame
ToggleButton.BorderSizePixel = 2
ToggleButton.BorderColor3 = Color3.fromRGB(0, 255, 170)

-- Reopen Button (Small GUI when minimized)
local ReopenButton = Instance.new("TextButton")
ReopenButton.Size = UDim2.new(0, 50, 0, 50)
ReopenButton.Position = UDim2.new(0.5, -25, 0.1, 0)
ReopenButton.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
ReopenButton.Text = "Open"
ReopenButton.TextColor3 = Color3.fromRGB(0, 255, 170)
ReopenButton.Font = Enum.Font.SourceSansBold
ReopenButton.TextSize = 14
ReopenButton.Parent = ScreenGui
ReopenButton.Visible = false
ReopenButton.Active = true
ReopenButton.Draggable = true

-- Minimize Functionality
MinimizeButton.MouseButton1Click:Connect(function()
    MainFrame.Visible = false
    ReopenButton.Visible = true
end)

-- Reopen Functionality
ReopenButton.MouseButton1Click:Connect(function()
    MainFrame.Visible = true
    ReopenButton.Visible = false
end)

-- Toggle AimLock
ToggleButton.MouseButton1Click:Connect(function()
    AimLock = not AimLock
    ToggleButton.Text = "AimLock: " .. (AimLock and "ON" or "OFF")
    ToggleButton.TextColor3 = AimLock and Color3.fromRGB(0, 255, 0) or Color3.fromRGB(255, 0, 0)
end)

-- Function to Spoof Camera Updates (Byfron and TSB Bypass Attempt)
local function SpoofCamera(TargetPosition)
    -- Simulate human-like camera movement with random micro-adjustments
    local spoofOffset = Vector3.new(
        math.sin(tick()) * math.random(-0.2, 0.2), -- Sinusoidal variation for natural sway
        math.cos(tick()) * math.random(-0.1, 0.1),
        math.random(-0.05, 0.05)
    )
    SpoofedMouseOffset = spoofOffset
    return TargetPosition + spoofOffset
end

-- Function to Randomize Execution Timing (Byfron Timing Check Bypass)
local function RandomizeExecution()
    -- Introduce randomized delays to break predictable execution patterns
    local delayTime = math.random(RandomDelayMin, RandomDelayMax)
    wait(delayTime)
end

-- Function to Simulate Mouse Input (Byfron and TSB Input Detection Bypass)
local function SimulateMouseInput(TargetPos)
    -- Simulate fake mouse movement to mimic human input
    -- This assumes an exploit environment with input simulation (e.g., Synapse X)
    if syn and syn.mouse1click then
        local fakeMousePos = Vector2.new(
            Camera.ViewportSize.X * (0.5 + math.random(-0.1, 0.1)),
            Camera.ViewportSize.Y * (0.5 + math.random(-0.1, 0.1))
        )
        syn.mouse_move(fakeMousePos.X, fakeMousePos.Y) -- Simulate mouse movement
        wait(math.random(0.01, FakeInputDelay)) -- Random delay for input
    end
end

-- Function to Hook Network Calls (TSB Anti-Cheat Bypass)
local function HookNetwork(Target)
    -- Attempt to intercept and modify network packets to mask aim behavior
    -- This uses a pseudo-implementation based on common exploit methods
    if syn and syn.request then
        -- Hook into RemoteEvents or RemoteFunctions if they exist
        for _, remote in pairs(game.ReplicatedStorage:GetDescendants()) do
            if remote:IsA("RemoteEvent") or remote:IsA("RemoteFunction") then
                -- Wrap remote calls with a secure proxy to hide aim data
                local oldNameCall = getrawmetatable(game).__namecall
                setrawmetatable(game, {
                    __namecall = newcclosure(function(self, ...)
                        local args = {...}
                        -- Check if the call involves aim or camera data
                        if self == remote and table.find(args, "Aim") or table.find(args, "Camera") then
                            -- Spoof the data being sent to server
                            for i, arg in pairs(args) do
                                if typeof(arg) == "Vector3" or typeof(arg) == "CFrame" then
                                    args[i] = arg + SpoofedMouseOffset -- Add fake offset
                                end
                            end
                        end
                        return oldNameCall(self, unpack(args))
                    end)
                })
            end
        end
    end
end

-- Function to Spoof Memory Signatures (Byfron Detection Bypass)
local function SpoofMemory()
    -- Attempt to hide script execution from memory scans
    -- This is pseudo-code for exploit environments with memory manipulation
    if syn and syn.protect_gui then
        syn.protect_gui(ScreenGui) -- Protect GUI from detection
    end
    -- Randomize script name and parent to avoid static signature detection
    ScreenGui.Name = "CoreGui_" .. tostring(math.random(1000, 9999))
end

-- Function to Get Closest Player
local function GetClosestPlayer()
    local ClosestPlayer = nil
    local ShortestDistance = math.huge

    for _, Player in pairs(Players:GetPlayers()) do
        if Player ~= LocalPlayer and Player.Character and Player.Character:FindFirstChild(TargetPart) then
            local TargetPos = Player.Character[TargetPart].Position
            local Distance = (Camera.CFrame.Position - TargetPos).Magnitude
            
            if Distance < ShortestDistance and Distance <= FOV then
                local Humanoid = Player.Character:FindFirstChild("Humanoid")
                if Humanoid and Humanoid.Health > 0 then
                    ShortestDistance = Distance
                    ClosestPlayer = Player
                end
            end
        end
    end
    return ClosestPlayer
end

-- Aim Lock Logic with Anti-Cheat Measures
RunService.RenderStepped:Connect(function()
    if AimLock then
        RandomizeExecution() -- Break timing patterns for Byfron
        SpoofMemory() -- Attempt memory signature spoofing
        local Target = GetClosestPlayer()
        if Target and Target.Character and Target.Character:FindFirstChild(TargetPart) then
            local TargetPos = Target.Character[TargetPart].Position
            local SpoofedPos = SpoofCamera(TargetPos) -- Add human-like offset
            SimulateMouseInput(SpoofedPos) -- Simulate fake mouse input
            HookNetwork(Target) -- Attempt to mask network data for TSB

            -- Smooth camera movement using lerp
            local CurrentCFrame = Camera.CFrame
            local TargetCFrame = CFrame.new(CurrentCFrame.Position, SpoofedPos)
            local LerpedCFrame = CurrentCFrame:Lerp(TargetCFrame, Smoothness)
            Camera.CFrame = LerpedCFrame
        end
    end
end)

-- Optional: Toggle with Keybind 'E' as Backup
UserInputService.InputBegan:Connect(function(Input)
    if Input.KeyCode == Enum.KeyCode.E then
        AimLock = not AimLock
        ToggleButton.Text = "AimLock: " .. (AimLock and "ON" or "OFF")
        ToggleButton.TextColor3 = AimLock and Color3.fromRGB(0, 255, 0) or Color3.fromRGB(255, 0, 0)
    end
end)
