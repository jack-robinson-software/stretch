import AppKit
import QuartzCore

final class StretchApp: NSObject, NSApplicationDelegate {
    let companion = CompanionCharacter.pip
    let preferences = Preferences()
    var session = Session()
    let store: FrameStore
    let root = CompanionRoot(frame: NSRect(x: 0,y: 0,width: 448,height: 260))
    let panel = CompanionPanel(contentRect: NSRect(x: 0,y: 0,width: 448,height: 260), styleMask: [.borderless,.nonactivatingPanel], backing: .buffered, defer: false)
    lazy var character = CharacterView(store: store)
    lazy var bubble = SpeechBubble(target: self, first: #selector(firstAction), second: #selector(secondAction), later: #selector(notNow))
    var status: NSStatusItem!
    var clock: Timer?
    var mouseCheck: Timer?
    var nextNudge: Date?
    var sequence = 0
    var welcome: NSWindow?
    var toggle: CompanionButton?
    var statusLabel: NSTextField?
    var intervalControl: NSSegmentedControl?
    var hoursControl: NSPopUpButton?
    var captureDirectory: String?
    init(resources: URL) { store = FrameStore(resources); super.init() }
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        panel.isOpaque = false; panel.backgroundColor = .clear; panel.hasShadow = false; panel.level = .floating; panel.hidesOnDeactivate = false
        panel.collectionBehavior = [.canJoinAllSpaces,.fullScreenAuxiliary]; panel.contentView = root
        root.addSubview(character); root.addSubview(bubble); bubble.eyebrow.stringValue = companion.name.uppercased()
        character.progress = { [weak self] p in self?.bubble.progress.fraction = p }
        setUpMenu()
        NotificationCenter.default.addObserver(self,selector:#selector(reposition),name:NSApplication.didChangeScreenParametersNotification,object:nil)
        NSWorkspace.shared.notificationCenter.addObserver(self,selector:#selector(woke),name:NSWorkspace.didWakeNotification,object:nil)
        let timer = Timer(timeInterval: 15,repeats:true) { [weak self] _ in self?.tick() }; clock = timer; RunLoop.main.add(timer,forMode:.common)
        let mouse = Timer(timeInterval: 0.08,repeats:true) { [weak self] _ in self?.updateMousePassthrough() }; mouseCheck = mouse; RunLoop.main.add(mouse,forMode:.common)
        if preferences.enabled { scheduleNext() }
        if let i = CommandLine.arguments.firstIndex(of:"--capture"), CommandLine.arguments.count > i+1 {
            captureDirectory = CommandLine.arguments[i+1]
            DispatchQueue.main.asyncAfter(deadline:.now()+0.5) { self.captureViews(); NSApp.terminate(nil) }; return
        }
        if !preferences.defaults.bool(forKey:"hasMetPip") || CommandLine.arguments.contains("--welcome") {
            preferences.defaults.set(true,forKey:"hasMetPip"); showSettings(nil)
        }
        DispatchQueue.main.asyncAfter(deadline:.now()+0.55) { self.sayHello(nil) }
    }
    func setUpMenu() {
        status = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        let icon = NSImage(size:NSSize(width:18,height:20)); icon.lockFocus(); NSColor.black.setFill()
        let path = NSBezierPath(); path.move(to:NSPoint(x:8,y:1)); path.curve(to:NSPoint(x:3,y:14),controlPoint1:NSPoint(x:0,y:2),controlPoint2:NSPoint(x:1,y:10)); path.curve(to:NSPoint(x:12,y:19),controlPoint1:NSPoint(x:5,y:21),controlPoint2:NSPoint(x:11,y:21)); path.curve(to:NSPoint(x:13,y:11),controlPoint1:NSPoint(x:15,y:17),controlPoint2:NSPoint(x:11,y:14)); path.curve(to:NSPoint(x:8,y:1),controlPoint1:NSPoint(x:20,y:4),controlPoint2:NSPoint(x:15,y:0)); path.close(); path.fill()
        if let context = NSGraphicsContext.current?.cgContext { context.saveGState(); context.setBlendMode(.clear); context.fillEllipse(in:NSRect(x:6,y:11,width:1.7,height:2.5)); context.fillEllipse(in:NSRect(x:10,y:12,width:1.7,height:2.5)); context.restoreGState() }
        icon.unlockFocus(); icon.isTemplate = true; status.button?.image = icon; status.button?.toolTip = "\(AppIdentity.name) — a little nudge with \(companion.name)"
        rebuildMenu()
    }
    func rebuildMenu() {
        let menu = NSMenu()
        func add(_ title: String,_ selector: Selector?,enabled: Bool = true) { let item = NSMenuItem(title:title,action:selector,keyEquivalent:""); item.target = self; item.isEnabled = enabled; menu.addItem(item) }
        menu.autoenablesItems = false
        add(statusText(),nil,enabled:false); menu.addItem(.separator())
        add("Say hello",#selector(sayHello(_:))); add("Try a seated pause",#selector(trySeated)); add("Try a standing pause",#selector(tryStanding)); menu.addItem(.separator())
        add("Snooze for 15 minutes",#selector(snoozeMenu),enabled:preferences.enabled)
        add(preferences.enabled ? "Pause nudges" : "Turn on nudges",#selector(toggleReminders)); add("Settings…",#selector(showSettings(_:))); menu.addItem(.separator()); add("Quit \(AppIdentity.name)",#selector(quit))
        status.menu = menu
    }
    func statusText() -> String {
        guard preferences.enabled else { return "Nudges are paused" }
        guard let nextNudge else { return "A little pause, every \(preferences.interval) minutes" }
        let f = DateFormatter(); f.dateStyle = Calendar.current.isDateInToday(nextNudge) ? .none : .short; f.timeStyle = .short
        return "Next little nudge: \(f.string(from:nextNudge))"
    }
    @objc func reposition() {
        guard let screen = NSScreen.main ?? NSScreen.screens.first else { return }; let safe = screen.visibleFrame
        panel.setFrameOrigin(NSPoint(x:safe.maxX-panel.frame.width-14,y:safe.maxY-panel.frame.height-12))
    }
    @objc func woke() { if preferences.enabled { scheduleNext() } }
    func showPanel() {
        reposition(); panel.alphaValue = 1; bubble.alphaValue = 1; bubble.isHidden = false
        let wasVisible = panel.isVisible
        panel.orderFrontRegardless()
        if !wasVisible { panel.alphaValue = 0; NSAnimationContext.runAnimationGroup { ctx in ctx.duration = 0.24; panel.animator().alphaValue = 1 } }
    }
    func updateMousePassthrough() {
        guard panel.isVisible else { return }
        let global = NSEvent.mouseLocation; let local = NSPoint(x:global.x-panel.frame.minX,y:global.y-panel.frame.minY)
        panel.ignoresMouseEvents = bubble.isHidden || !bubble.frame.insetBy(dx:8,dy:8).contains(local)
    }
    @objc func sayHello(_ sender: Any?) {
        sequence += 1; let token = sequence; session.invite(); bubble.show(session.phase); showPanel()
        character.play(.wave,repeats:1) { [weak self] in guard let self, self.sequence == token else { return }; self.character.play(.idle) }
        DispatchQueue.main.asyncAfter(deadline:.now()+25) { [weak self] in guard let self, self.sequence == token, self.session.phase == .invitation else { return }; self.notNow() }
    }
    @objc func trySeated() { start(.seated) }
    @objc func tryStanding() { start(.standing) }
    func start(_ kind: Kind) {
        sequence += 1; let token = sequence; let movement = session.choose(kind); bubble.show(session.phase); bubble.progress.fraction = 0; showPanel()
        character.play(movement.clip,repeats:2) { [weak self] in guard let self, self.sequence == token else { return }; self.finish() }
    }
    @objc func firstAction() {
        switch session.phase { case .invitation: start(.seated); case .movement(let m): start(m.kind); case .completed(let kind): start(kind); default: break }
    }
    @objc func secondAction() {
        switch session.phase { case .invitation: start(.standing); case .movement: finish(); case .completed: leave(); default: break }
    }
    func finish() {
        guard case .movement(let m) = session.phase else { return }; sequence += 1; let token = sequence; session.finish(); bubble.show(session.phase)
        if m.kind == .seated { character.freeze(.seatedReach) } else { character.play(.celebrate,repeats:1) }
        DispatchQueue.main.asyncAfter(deadline:.now()+3) { [weak self] in guard let self, self.sequence == token else { return }; self.leaveWhenReady(token) }
    }
    func leaveWhenReady(_ token: Int) {
        guard sequence == token else { return }
        let mouse = NSEvent.mouseLocation; let point = NSPoint(x:mouse.x-panel.frame.minX,y:mouse.y-panel.frame.minY)
        if bubble.frame.contains(point) { DispatchQueue.main.asyncAfter(deadline:.now()+0.5) { [weak self] in self?.leaveWhenReady(token) }; return }
        leave()
    }
    func leave() {
        let seated: Bool; if case .completed(let kind) = session.phase { seated = kind == .seated } else { seated = false }
        sequence += 1; let token = sequence; session.phase = .leaving; bubble.isHidden = true; panel.ignoresMouseEvents = true
        if seated { hidePanel(); return }
        character.play(.walkOff,repeats:1) { [weak self] in guard let self, self.sequence == token else { return }; self.hidePanel() }
    }
    @objc func notNow() {
        if preferences.enabled { nextNudge = Schedule.next(after:Date(),minutes:15,hours:preferences.hours) }
        hidePanel(reschedule:false)
    }
    func hidePanel(reschedule: Bool = true) {
        sequence += 1; let token = sequence; session.hide(); character.stop(); panel.ignoresMouseEvents = true
        NSAnimationContext.runAnimationGroup({ ctx in ctx.duration = 0.22; panel.animator().alphaValue = 0 },completionHandler:{ [weak self] in guard let self, self.sequence == token else { return }; self.panel.orderOut(nil) })
        if reschedule && preferences.enabled { scheduleNext() }; updateSettings(); rebuildMenu()
    }
    func scheduleNext() { nextNudge = Schedule.next(after:Date(),minutes:preferences.interval,hours:preferences.hours); updateSettings(); rebuildMenu() }
    func tick() {
        if preferences.enabled, let nextNudge, Date() >= nextNudge {
            if session.phase == .hidden && preferences.hours.permits(Date()) { sayHello(nil) }
            scheduleNext()
        }
        statusLabel?.stringValue = statusText()
    }
    @objc func snoozeMenu() { nextNudge = Schedule.next(after:Date(),minutes:15,hours:preferences.hours); hidePanel(reschedule:false) }
    @objc func toggleReminders() {
        preferences.enabled.toggle(); if preferences.enabled { scheduleNext() } else { nextNudge = nil }; updateSettings(); rebuildMenu()
    }
    @objc func intervalChanged(_ sender: NSSegmentedControl) { preferences.interval = [15,30,45,60][max(0,sender.selectedSegment)]; if preferences.enabled { scheduleNext() }; updateSettings() }
    @objc func hoursChanged(_ sender: NSPopUpButton) { preferences.hours = WorkHours.allCases[max(0,sender.indexOfSelectedItem)]; if preferences.enabled { scheduleNext() } }
    @objc func quit() { NSApp.terminate(nil) }
    @objc func showSettings(_ sender: Any?) {
        if let welcome { welcome.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps:true); return }
        let w = NSWindow(contentRect:NSRect(x:0,y:0,width:530,height:520),styleMask:[.titled,.closable,.miniaturizable,.fullSizeContentView],backing:.buffered,defer:false)
        w.title = AppIdentity.name; w.titlebarAppearsTransparent = true; w.backgroundColor = Palette.paper; w.isReleasedWhenClosed = false
        let content = NSView(frame:NSRect(x:0,y:0,width:530,height:520)); w.contentView = content
        func put(_ text: String,_ frame: NSRect,_ font: NSFont,_ color: NSColor = Palette.cocoa) { let v = label(text,font:font,color:color); v.frame = frame; content.addSubview(v) }
        put("\(AppIdentity.name.uppercased()) • MEET \(companion.name.uppercased())",NSRect(x:34,y:435,width:310,height:15),.systemFont(ofSize:10,weight:.semibold),Palette.muted)
        put("A tiny pause.\nA little better.",NSRect(x:32,y:344,width:310,height:85),serif(31))
        put("A wave, a stretch, then back to your day.\n\(companion.name) pops by quietly, on your terms.",NSRect(x:34,y:289,width:320,height:45),.systemFont(ofSize:14),Palette.muted)
        let hero = NSImageView(frame:NSRect(x:370,y:315,width:118,height:142)); if let cg = store.image(.idle,0) { hero.image = NSImage(cgImage:cg,size:NSSize(width:300,height:360)) }; hero.imageScaling = .scaleProportionallyUpOrDown; content.addSubview(hero)
        let hello = CompanionButton("Say hello",style:.primary,target:self,action:#selector(sayHello(_:))); hello.frame = NSRect(x:34,y:235,width:139,height:37); content.addSubview(hello)
        let seated = CompanionButton("Try a seated pause",target:self,action:#selector(trySeated)); seated.frame = NSRect(x:184,y:235,width:151,height:37); content.addSubview(seated)
        let line = NSBox(frame:NSRect(x:34,y:214,width:462,height:1)); line.boxType = .separator; content.addSubview(line)
        put("Your rhythm",NSRect(x:34,y:174,width:200,height:25),serif(19))
        put("A little nudge every",NSRect(x:34,y:139,width:175,height:20),.systemFont(ofSize:13),Palette.muted)
        let segments = NSSegmentedControl(labels:["15m","30m","45m","60m"],trackingMode:.selectOne,target:self,action:#selector(intervalChanged(_:))); segments.frame = NSRect(x:262,y:135,width:234,height:28); content.addSubview(segments); intervalControl = segments
        put("Working hours",NSRect(x:34,y:102,width:175,height:20),.systemFont(ofSize:13),Palette.muted)
        let hours = NSPopUpButton(frame:NSRect(x:317,y:98,width:179,height:28),pullsDown:false); hours.addItems(withTitles:WorkHours.allCases.map(\.label)); hours.target = self; hours.action = #selector(hoursChanged(_:)); content.addSubview(hours); hoursControl = hours
        let toggle = CompanionButton("Turn on gentle nudges",style:.primary,target:self,action:#selector(toggleReminders)); toggle.frame = NSRect(x:34,y:42,width:220,height:36); content.addSubview(toggle); self.toggle = toggle
        let status = label("Nudges are paused",font:.systemFont(ofSize:11),color:Palette.muted); status.frame = NSRect(x:268,y:40,width:228,height:35); content.addSubview(status); statusLabel = status
        put("Silent by default. Everything stays on your Mac.",NSRect(x:34,y:12,width:460,height:16),.systemFont(ofSize:10),Palette.muted)
        welcome = w; updateSettings(); w.center(); w.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps:true)
    }
    func updateSettings() {
        toggle?.title = preferences.enabled ? "Pause gentle nudges" : "Turn on gentle nudges"; toggle?.setAccessibilityLabel(toggle?.title); toggle?.needsDisplay = true
        statusLabel?.stringValue = statusText(); intervalControl?.selectedSegment = [15,30,45,60].firstIndex(of:preferences.interval) ?? 2
        hoursControl?.selectItem(at:WorkHours.allCases.firstIndex(of:preferences.hours) ?? 2)
    }
    func captureViews() {
        guard let directory = captureDirectory else { return }; try? FileManager.default.createDirectory(atPath:directory,withIntermediateDirectories:true)
        let scenes: [(String,Phase,Clip,Int)] = [("invitation",.invitation,.wave,50),("seated",.movement(.seatedReach),.seatedReach,78),("standing",.movement(.standingStretch),.stretch,132),("complete",.completed(.seated),.seatedReach,0)]
        for (name,phase,clip,frame) in scenes {
            session.phase = phase; bubble.show(phase); bubble.progress.fraction = 0.38; character.freeze(clip,frame:frame); bubble.isHidden = false; panel.alphaValue = 1; panel.orderFrontRegardless(); root.layoutSubtreeIfNeeded(); root.displayIfNeeded()
            if let rep = root.bitmapImageRepForCachingDisplay(in:root.bounds) { root.cacheDisplay(in:root.bounds,to:rep); if let data = rep.representation(using:.png,properties:[:]) { try? data.write(to:URL(fileURLWithPath:directory).appendingPathComponent(name+".png")) } }
        }
        showSettings(nil)
        if let view = welcome?.contentView, let rep = view.bitmapImageRepForCachingDisplay(in:view.bounds) { view.cacheDisplay(in:view.bounds,to:rep); if let data = rep.representation(using:.png,properties:[:]) { try? data.write(to:URL(fileURLWithPath:directory).appendingPathComponent("settings.png")) } }
        print("CAPTURED NATIVE VIEWS",directory)
    }
}
