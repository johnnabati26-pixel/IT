-- // Premium UI Library 2025 - "NEXUS UI" (Better than Rayfield) \\
-- Made by Grok with love for the Roblox devs who want the absolute best

local NexusUI = {
    Theme = {
        Accent = Color3.fromRGB(0, 170, 255),
        Background = Color3.fromRGB(20, 20, 30),
        Secondary = Color3.fromRGB(35, 35, 50),
        Text = Color3.fromRGB(255, 255, 255),
        Success = Color3.fromRGB(0, 255, 140),
        Warning = Color3.fromRGB(255, 200, 0),
        Danger = Color3.fromRGB(255, 60, 80)
    }
}

local TweenService = game:GetService("TweenService")
local UserInputService = game:GetService("UserInputService")
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local player = Players.LocalPlayer

-- Main ScreenGui
local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "NexusUI"
ScreenGui.ResetOnSpawn = false
ScreenGui.Parent = game.CoreGui

-- Floating Orb (Minimized State)
local FloatOrb = Instance.new("ImageLabel")
FloatOrb.Name = "FloatOrb"
FloatOrb.Size = UDim2.new(0, 60, 0, 60)
FloatOrb.Position = UDim2.new(0, 50, 0.5, -30)
FloatOrb.BackgroundTransparency = 0.1
FloatOrb.BackgroundColor3 = NexusUI.Theme.Accent
FloatOrb.Image = "rbxassetid://18358093674" -- Modern orb icon (or use circle with gradient)
FloatOrb.BorderSizePixel = 0
FloatOrb.Visible = false
FloatOrb.ZIndex = 999
FloatOrb.Parent = ScreenGui

-- Corner & Shadow for Orb
Instance.new("UICorner", FloatOrb).CornerRadius = UDim.new(1, 0)
local orbShadow = Instance.new("UIStroke", FloatOrb)
orbShadow.Thickness = 4
orbShadow.Color = Color3.new(0, 0, 0)
orbShadow.Transparency = 0.7
orbShadow.ApplyStrokeMode = Enum.ApplyStrokeMode.Border

-- Main Window
local MainFrame = Instance.new("Frame")
MainFrame.Name = "MainWindow"
MainFrame.Size = UDim2.new(0, 650, 0, 500)
MainFrame.Position = UDim2.new(0.5, -325, 0.5, -250)
MainFrame.BackgroundColor3 = NexusUI.Theme.Background
MainFrame.BorderSizePixel = 0
MainFrame.ClipsDescendants = true
MainFrame.Visible = true
MainFrame.Parent = ScreenGui

local MainCorner = Instance.new("UICorner", MainFrame)
MainCorner.CornerRadius = UDim.new(0, 16)

local MainStroke = Instance.new("UIStroke", MainFrame)
MainStroke.Color = NexusUI.Theme.Accent
MainStroke.Thickness = 2
MainStroke.Transparency = 0.5

-- Acrylic/Glass Effect (Backdrop Blur Simulation)
local BlurBackdrop = Instance.new("Frame", MainFrame)
BlurBackdrop.Size = UDim2.new(1, 0, 1, 0)
BlurBackdrop.BackgroundTransparency = 0.6
BlurBackdrop.BackgroundColor3 = Color3.new(1,1,1)
BlurBackdrop.ZIndex = -1

local AcrylicGradient = Instance.new("UIGradient", BlurBackdrop)
AcrylicGradient.Color = ColorSequence.new{
    ColorSequenceKeypoint.new(0, Color3.new(1,1,1)),
    ColorSequenceKeypoint.new(1, Color3.fromRGB(80,80,120))
}
AcrylicGradient.Rotation = 90
AcrylicGradient.Transparency = NumberSequence.new{
    NumberSequenceKeypoint.new(0, 0.7),
    NumberSequenceKeypoint.new(1, 0.9)
}

-- Title Bar
local TitleBar = Instance.new("Frame")
TitleBar.Name = "TitleBar"
TitleBar.Size = UDim2.new(1, 0, 0, 50)
TitleBar.BackgroundColor3 = Color3.new(0,0,0)
TitleBar.BackgroundTransparency = 0.4
TitleBar.Parent = MainFrame

local Title = Instance.new("TextLabel")
Title.Text = "NEXUS UI - Premium"
Title.Font = Enum.Font.GothamBold
Title.TextSize = 18
Title.TextColor3 = Color3.new(1,1,1)
Title.BackgroundTransparency = 1
Title.Size = UDim2.new(1, -140, 1, 0)
Title.Position = UDim2.new(0, 15, 0, 0)
Title.TextXAlignment = Enum.TextXAlignment.Left
Title.Parent = TitleBar

-- Minimize Button (-)
local MinimizeBtn = Instance.new("TextButton")
MinimizeBtn.Size = UDim2.new(0, 40, 0, 40)
MinimizeBtn.Position = UDim2.new(1, -90, 0, 5)
MinimizeBtn.BackgroundTransparency = 1
MinimizeBtn.Text = "—"
MinimizeBtn.TextColor3 = Color3.new(1,1,1)
MinimizeBtn.Font = Enum.Font.GothamBold
MinimizeBtn.TextSize = 28
MinimizeBtn.Parent = TitleBar

-- Close Button (X)
local CloseBtn = Instance.new("TextButton")
CloseBtn.Size = UDim2.new(0, 40, 0, 40)
CloseBtn.Position = UDim2.new(1, -45, 0, 5)
CloseBtn.BackgroundTransparency = 1
CloseBtn.Text = "✕"
CloseBtn.TextColor3 = Color3.new(1,1,1)
CloseBtn.Font = Enum.Font.GothamBold
CloseBtn.TextSize = 22
CloseBtn.Parent = TitleBar

-- Hover Effects
local function HoverEffect(button, color)
    button.MouseEnter:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.2), {TextColor3 = color}):Play()
    end)
    button.MouseLeave:Connect(function()
        TweenService:Create(button, TweenInfo.new(0.2), {TextColor3 = Color3.new(1,1,1)}):Play()
    end)
end

HoverEffect(MinimizeBtn, NexusUI.Theme.Accent)
HoverEffect(CloseBtn, NexusUI.Theme.Danger)

-- Dragging Functionality
local dragging = false
local dragInput
local dragStart
local startPos

local function updateInput(input, frame)
    local delta = input.Position - dragStart
    TweenService:Create(frame, TweenInfo.new(0.15), {Position = UDim2.new(startPos.X.Scale, startPos.X.Offset + delta.X, startPos.Y.Scale, startPos.Y.Offset + delta.Y)}):Play()
end

local function makeDraggable(frame)
    frame.InputBegan:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseButton1 then
            dragging = true
            dragStart = input.Position
            startPos = frame.Position

            input.Changed:Connect(function()
                if input.UserInputState == Enum.UserInputState.End then
                    dragging = false
                end
            end)
        end
    end)

    frame.InputChanged:Connect(function(input)
        if input.UserInputType == Enum.UserInputType.MouseMovement then
            dragInput = input
        end
    end)

    UserInputService.InputChanged:Connect(function(input)
        if dragging and (input == dragInput) then
            updateInput(input, frame)
        end
    end)
end

makeDraggable(TitleBar) -- Main window draggable
makeDraggable(FloatOrb)  -- Orb draggable

-- Minimize / Restore Logic
local isMinimized = false

MinimizeBtn.MouseButton1Click:Connect(function()
    if isMinimized then
        -- Restore
        MainFrame.Visible = true
        FloatOrb.Visible = false
        TweenService:Create(MainFrame, TweenInfo.new(0.4, Enum.EasingStyle.Quint), {Size = UDim2.new(0, 650, 0, 500)}):Play()
        TweenService:Create(MainFrame, TweenInfo.new(0.3), {BackgroundTransparency = 0}):Play()
        isMinimized = false
    else
        -- Minimize (keeps all scripts running!)
        TweenService:Create(MainFrame, TweenInfo.new(0.4, Enum.EasingStyle.Quint), {Size = UDim2.new(0, 0, 0, 0)}):Play()
        task.wait(0.3)
        MainFrame.Visible = false
        FloatOrb.Visible = true
        isMinimized = true
    end
end)

FloatOrb.MouseButton1Click:Connect(function()
    if isMinimized then
        MainFrame.Visible = true
        FloatOrb.Visible = false
        TweenService:Create(MainFrame, TweenInfo.new(0.4, Enum.EasingStyle.Quint), {Size = UDim2.new(0, 650, 0, 500)}):Play()
        isMinimized = false
    end
end)

-- Close Button - Fully destroys everything
CloseBtn.MouseButton1Click:Connect(function()
    TweenService:Create(MainFrame, TweenInfo.new(0.3), {BackgroundTransparency = 1}):Play()
    TweenService:Create(FloatOrb, TweenInfo.new(0.3), {BackgroundTransparency = 1}):Play()
    task.wait(0.35)
    ScreenGui:Destroy()
    -- All scripts that were running will STOP if they were children or connected to GUI
end)

-- Example Tab System (You can expand this)
local TabContainer = Instance.new("ScrollingFrame")
TabContainer.Size = UDim2.new(1, -20, 1, -70)
TabContainer.Position = UDim2.new(0, 10, 0, 60)
TabContainer.BackgroundTransparency = 1
TabContainer.ScrollBarThickness = 4
TabContainer.Parent = MainFrame

-- Public Functions
function NexusUI:CreateTab(name)
    local TabButton = Instance.new("TextButton")
    TabButton.Size = UDim2.new(0, 140, 0, 40)
    TabButton.BackgroundColor3 = NexusUI.Theme.Secondary
    TabButton.Text = name
    TabButton.TextColor3 = NexusUI.Theme.Text
    TabButton.Font = Enum.Font.GothamSemibold
    TabButton.Parent = MainFrame

    -- Add more features like buttons, toggles, sliders, etc. here
    -- This is just the base - you can extend it infinitely

    return {
        AddButton = function(self, text, callback)
            -- Your button creation here
        end,
        AddToggle = function(self, text, default, callback)
            -- Your toggle here
        end
    }
end

-- Return the library
MainFrame.Visible = true
FloatOrb.Visible = false

return NexusUI
